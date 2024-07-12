import customtkinter as ctk
from tkinter import messagebox
import requests
import threading

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class FileTransferApp:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer Tool")
        master.geometry("500x600")
        master.resizable(True, True)

        # Configure grid layout
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(master, corner_radius=10)
        self.main_frame.grid(pady=20, padx=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame, text="File Transfer Tool", font=("Arial", 24, "bold")
        )
        self.header_label.grid(row=0, column=0, pady=10, sticky="n")

        # Step 1: Enter Pixeldrain File ID
        self.step1_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.step1_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        self.step1_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.step1_frame,
            text="Step 1: Enter Pixeldrain File ID",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, pady=(10, 0), sticky="w")
        self.pixeldrain_id_entry = ctk.CTkEntry(self.step1_frame)
        self.pixeldrain_id_entry.grid(row=1, column=0, pady=(5, 10), sticky="ew")

        # Step 2: Enter Buzzheavier Folder ID
        self.step2_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.step2_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        self.step2_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.step2_frame,
            text="Step 2: Enter Buzzheavier Folder ID",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, pady=(10, 0), sticky="w")
        self.buzzheavier_folder_entry = ctk.CTkEntry(self.step2_frame)
        self.buzzheavier_folder_entry.grid(row=1, column=0, pady=(5, 10), sticky="ew")

        # Step 3: Enter Buzzheavier API Key
        self.step3_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.step3_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.step3_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.step3_frame,
            text="Step 3: Enter Buzzheavier API Key",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, pady=(10, 0), sticky="w")
        self.buzzheavier_api_entry = ctk.CTkEntry(self.step3_frame, show="*")
        self.buzzheavier_api_entry.grid(row=1, column=0, pady=(5, 20), sticky="ew")

        # Progress Bar
        self.progress_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.progress_frame.grid(row=4, column=0, pady=10, padx=20, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame, text="Progress:", font=("Arial", 14)
        )
        self.progress_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        self.progress = ctk.CTkProgressBar(self.progress_frame)
        self.progress.grid(row=1, column=0, pady=(5, 10), sticky="ew")
        self.progress.set(0)

        # Status Label
        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 12))
        self.status_label.grid(row=5, column=0, pady=(10, 0), sticky="w")

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.button_frame.grid(row=6, column=0, pady=20, padx=20, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Transfer Button
        self.transfer_button = ctk.CTkButton(
            self.button_frame,
            text="Transfer File",
            command=self.start_transfer,
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=20,
            hover_color="#1f6aa5",
        )
        self.transfer_button.grid(row=0, column=0, pady=10, padx=5, sticky="ew")

        # Cancel Button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel Transfer",
            command=self.cancel_transfer,
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=20,
            hover_color="#a51f1f",
        )
        self.cancel_button.grid(row=0, column=1, pady=10, padx=5, sticky="ew")
        self.cancel_button.configure(state=ctk.DISABLED)

        # Flag to control upload
        self.cancel_flag = False

    def start_transfer(self):
        self.transfer_button.configure(state=ctk.DISABLED)
        self.cancel_button.configure(state=ctk.NORMAL)
        self.progress.set(0)
        self.status_label.configure(text="Starting transfer...")
        self.cancel_flag = False
        threading.Thread(target=self.transfer_file, daemon=True).start()

    def cancel_transfer(self):
        self.cancel_flag = True
        self.status_label.configure(text="Transfer canceled")
        self.transfer_button.configure(state=ctk.NORMAL)
        self.cancel_button.configure(state=ctk.DISABLED)

    def transfer_file(self):
        pixeldrain_file_id = self.pixeldrain_id_entry.get()
        buzzheavier_folder_id = self.buzzheavier_folder_entry.get()
        buzzheavier_api_key = self.buzzheavier_api_entry.get()

        if not all([pixeldrain_file_id, buzzheavier_folder_id, buzzheavier_api_key]):
            self.show_error("All fields are required!")
            return

        try:
            self.update_status("Fetching file info...")
            pixeldrain_info_url = (
                f"https://pixeldrain.com/api/file/{pixeldrain_file_id}/info"
            )
            response = requests.get(pixeldrain_info_url)
            response.raise_for_status()
            file_info = response.json()
            file_name = file_info["name"]
            file_size = file_info["size"]

            pixeldrain_download_url = (
                f"https://pixeldrain.com/api/file/{pixeldrain_file_id}"
            )

            buzzheavier_upload_url = f"https://w.buzzheavier.com/{file_name}?folderId={buzzheavier_folder_id}"
            headers = {"Authorization": f"Bearer {buzzheavier_api_key}"}

            self.update_status("Transferring file...")

            with requests.get(pixeldrain_download_url, stream=True) as source:
                source.raise_for_status()
                with requests.put(
                    buzzheavier_upload_url,
                    data=self.stream_file(source, file_size),
                    headers=headers,
                ) as destination:
                    destination.raise_for_status()

            if not self.cancel_flag:
                self.update_status("Transfer completed successfully!")
                self.progress.set(1)
                messagebox.showinfo("Success", "File transfer completed successfully!")
            else:
                self.update_status("Transfer canceled")

        except requests.RequestException as e:
            if not self.cancel_flag:
                self.show_error(f"An error occurred: {str(e)}")

        finally:
            self.transfer_button.configure(state=ctk.NORMAL)
            self.cancel_button.configure(state=ctk.DISABLED)

    def stream_file(self, source, file_size):
        transferred_size = 0
        for chunk in source.iter_content(chunk_size=8192):
            if self.cancel_flag:
                break
            if chunk:
                transferred_size += len(chunk)
                self.update_progress(transferred_size, file_size)
                yield chunk

    def update_progress(self, transferred_size, total_size):
        progress = transferred_size / total_size
        print(f"Progress: {progress * 100:.2f}%")  # Debug print
        self.progress.set(progress)
        self.master.update_idletasks()

    def update_status(self, message):
        self.status_label.configure(text=message)
        self.master.update_idletasks()

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_label.configure(text="Transfer failed")
        self.transfer_button.configure(state=ctk.NORMAL)
        self.cancel_button.configure(state=ctk.DISABLED)


root = ctk.CTk()
app = FileTransferApp(root)
root.mainloop()
