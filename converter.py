import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import threading

class ImageToPdfConverter:
    def __init__(self, master):
        self.master = master
        master.title("Convertir des images en PDF")

        # Liste pour stocker les chemins des fichiers d'image sélectionnés
        self.image_paths = []

        # Titre du PDF
        self.pdf_title = ""

        # Barre de chargement
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")

        # Bouton pour sélectionner des fichiers
        self.select_button = tk.Button(master, text="Sélectionner des images", command=self.select_images)
        self.select_button.pack(pady=20)

        # Bouton pour convertir les images sélectionnées en PDF
        self.convert_button = tk.Button(master, text="Convertir", command=self.convert_images)
        self.convert_button.pack(pady=10)

        # Ajouter la barre de chargement
        self.progress_bar.pack(pady=10)

    def select_images(self):
        file_paths = filedialog.askopenfilenames(title="Sélectionner des fichiers d'image",
                                                  filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_paths:
            self.image_paths = file_paths
            print("Images sélectionnées : ", self.image_paths)

    def get_pdf_title(self):
        self.pdf_title = askstring("Titre du PDF", "Entrez le titre du PDF:")
        if not self.pdf_title:
            print("Titre du PDF non fourni.")
        else:
            print(f"Titre du PDF : {self.pdf_title}")

    def convert_images(self):
        if not self.image_paths:
            print("Aucune image sélectionnée.")
            return

        # Obtenir le titre du PDF
        self.get_pdf_title()
        if not self.pdf_title:
            return

        # Nom du fichier PDF de sortie
        output_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not output_pdf:
            print("Conversion annulée.")
            return

        # Désactiver les boutons pendant la conversion
        self.select_button.config(state=tk.DISABLED)
        self.convert_button.config(state=tk.DISABLED)

        # Initialiser la barre de chargement
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.image_paths)

        # Exécuter la conversion dans un thread séparé pour éviter le blocage de l'interface utilisateur
        conversion_thread = threading.Thread(target=self.perform_conversion, args=(output_pdf,))
        conversion_thread.start()

    def perform_conversion(self, output_pdf):
        try:
            # Créer un nouveau fichier PDF
            c = canvas.Canvas(output_pdf)

            # Ajouter le titre au PDF
            if self.pdf_title:
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 750, self.pdf_title)

            for index, image_path in enumerate(self.image_paths):
                try:
                    # Ouvrir l'image avec PIL pour vérifier la validité
                    img = Image.open(image_path)

                    # Réinitialiser le curseur pour assurer la lecture correcte de l'image
                    img.seek(0)

                    width, height = img.size

                    # Si la largeur est supérieure à la hauteur, diviser en deux pages (gauche et droite)
                    if width > height:
                        page1 = img.crop((0, 0, width / 2, height))


                        # Page gauche
                        c.setPageSize((width / 2, height))
                        c.drawInlineImage(page1, 0, 0, width / 2, height)
                        c.showPage()


                        page2 = img.crop((width / 2, 0, width, height))
                        # Page droite
                        c.setPageSize((width / 2, height))
                        c.drawInlineImage(page2,0, 0, width / 2, height)
                    else:
                        # Sinon, ajouter simplement la page normalement
                        c.setPageSize((width, height))
                        c.drawInlineImage(image_path, 0, 0, width, height)

                    # Ajouter une nouvelle page pour l'image suivante
                    c.showPage()

                    # Mettre à jour la barre de progression
                    self.progress_bar["value"] = index + 1
                    self.master.update_idletasks()  # Force la mise à jour de l'interface
                except Exception as e:
                    print(f"Erreur lors du traitement de l'image {image_path}: {e}")

            # Enregistrer le PDF
            c.save()

            # Modifier les métadonnées du PDF avec PyPDF2
            try:
                with open(output_pdf, 'rb+') as file:
                    reader = PdfReader(file)
                    writer = PdfWriter()

                    writer.append_pages_from_reader(reader)
                    metadata = reader.metadata
                    writer.add_metadata(metadata)

                    writer.add_metadata({
                        '/Author': "Votre auteur",  # Remplacez par l'auteur souhaité
                        '/Title': self.pdf_title,
                        '/Subject': "Votre sujet",  # Remplacez par le sujet souhaité
                        '/Producer': "CropPDF",
                        '/Creator': "CropPDF",
                    })

                    writer.write(file)
            except Exception as ex:
                print(f"Erreur lors de l'édition des métadonnées : {ex}")

            print(f"Le PDF a été créé avec succès : {output_pdf}")
        except Exception as ex:
            print(f"Erreur lors de la conversion en PDF : {ex}")
        finally:
            # Mettre à jour la barre de chargement à 100% après la conversion
            self.progress_bar["value"] = self.progress_bar["maximum"]
            # Réactiver les boutons après la conversion
            self.select_button.config(state=tk.NORMAL)
            self.convert_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPdfConverter(root)
    root.mainloop()
