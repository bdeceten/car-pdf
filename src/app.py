from tkinter import *
from tkinter import filedialog
from PyPDF2 import PdfFileReader, PdfFileWriter
import io
import reportlab.pdfgen.canvas as cv
import re


class App():

    def __init__(self):
        def getFilePath():
            global filePath
            filetypes = [('PDF files', '*.pdf')]
            filePath = filedialog.askopenfilename(
                title='Open a file', initialdir='/', filetypes=filetypes)
            if filePath != None and filePath != "":
                self.canvas.itemconfigure(
                    self.pdfText, text="Fichier sélectionné", fill="green")
            else:
                self.canvas.itemconfigure(
                    self.pdfText, text="Document de location\nrempli par le locataire (.pdf) :", fill="red")

        self.root = Tk()
        self.root.title('Car PDF')
        self.root.tk.call('wm', 'iconphoto', self.root._w,
                          PhotoImage(file='ressources/logo_ceten.png'))

        self.root.geometry('500x375')
        self.root.resizable(0, 0)

        self.canvas = Canvas(self.root, width=500, height=350)
        self.canvas.pack(fill="both", expand=True)

        self.prenomEntry = Entry(self.root, width=25)
        self.nomEntry = Entry(self.root, width=25)
        self.dateEntry = Entry(self.root, width=25)
        self.kmEntry = Entry(self.root, width=25)
        self.pdfEntry = Button(
            self.root, text="Sélectionner le fichier", command=getFilePath)

        self.prenomText = self.canvas.create_text(
            100, 50, text="Prénom du locataire :")
        self.nomText = self.canvas.create_text(
            100, 100, text="Nom du locataire :")
        self.dateText = self.canvas.create_text(
            100, 150, text="Date de location :")
        self.kmText = self.canvas.create_text(
            100, 200, text="Kilométrage à la\nremise des clés :")
        self.pdfText = self.canvas.create_text(
            100, 250, text="Document de location\nrempli par le locataire (.pdf) :")

        self.bienvenue = self.canvas.create_text(
            250, 15, text="Bienvenue sur Car PDF !")
        self.errorText = self.canvas.create_text(250, 330, text="", fill='red')
        self.credits = self.canvas.create_text(
            250, 360, text='Made by Louis THOMAS, promotion 2023')

        self.canvas.create_window(300, 50, window=self.prenomEntry)
        self.canvas.create_window(300, 100, window=self.nomEntry)
        self.canvas.create_window(300, 150, window=self.dateEntry)
        self.canvas.create_window(300, 200, window=self.kmEntry)
        self.canvas.create_window(300, 250, window=self.pdfEntry)

        self.button = Button(self.root, width=20,
                             command=self.CreatePDF, text="Générer le PDF de logistique")
        self.button.bind("<Return>", self.CreatePDF)

        self.canvas.create_window(250, 300, window=self.button)

        self.root.mainloop()

    def CreatePDF(self, event=None):
        nom = self.nomEntry.get()
        prenom = self.prenomEntry.get()
        date = self.dateEntry.get()
        km = self.kmEntry.get()
        pdf = filePath

        if nom == "" or prenom == "" or date == "" or km == "" or pdf == "":
            self.canvas.itemconfigure(
                self.errorText, text="Un ou plusieurs champs semblent être vides")
            return 0

        if not re.match(r"[0-9]{2}\/[0-9]{2}\/[0-9]{4}", date):
            self.canvas.itemconfigure(
                self.errorText, text="Le format de la date doit être JJ/MM/AAAA")
            return 0

        if not re.match(r"^[1-9][0-9]*$", km):
            self.canvas.itemconfigure(
                self.errorText, text="Le nombre de kilomètres doit être composé de chiffres uniquement")
            return 0
        try:
            pdfWriter = PdfFileWriter()

            # Entry PDF
            pdfFileObj = open(pdf, 'rb')
            pdfReader = PdfFileReader(pdfFileObj)

            xmax = float(pdfReader.getPage(0).mediaBox.getWidth())
            ymax = float(pdfReader.getPage(0).mediaBox.getHeight())

            # First Page
            packet = io.BytesIO()
            can = cv.Canvas(packet, pagesize=(xmax, ymax))
            can.setFontSize(10)
            can.drawString(xmax*0.60, ymax*0.28, km)
            can.drawString(xmax*0.33, ymax*0.183, date)
            can.save()
            packet.seek(0)
            packetReader = PdfFileReader(packet)

            pageObj = pdfReader.getPage(0)
            pageObj.merge_page(packetReader.getPage(0))
            pdfWriter.addPage(pageObj)

            # Second Page
            packet = io.BytesIO()
            can = cv.Canvas(packet, pagesize=(xmax, ymax))
            can.drawImage("ressources/signature.png", xmax*0.072,
                          ymax*0.193, height=ymax*0.084, width=ymax*0.084*808/263)
            can.save()
            packet.seek(0)
            packetReader = PdfFileReader(packet)

            pageObj = pdfReader.getPage(1)
            pageObj.merge_page(packetReader.getPage(0))
            pdfWriter.addPage(pageObj)

            # Ressources PDF
            packet = io.BytesIO()
            can = cv.Canvas(packet, pagesize=(xmax, ymax))
            can.setFontSize(10)
            can.drawString(xmax*0.145, ymax*0.888, date)
            can.drawString(xmax*0.203, ymax*0.852, prenom+" "+nom)
            can.drawString(xmax*0.282, ymax*0.818, km)
            can.save()
            packet.seek(0)
            packetReader = PdfFileReader(packet)

            pdfFileObj = open("ressources/etat-des-lieux_rempli.pdf", 'rb')
            pdfReader = PdfFileReader(pdfFileObj)

            pageObj = pdfReader.getPage(0)
            pageObj.merge_page(packetReader.getPage(0))
            pdfWriter.addPage(pageObj)

            # Output PDF
            pdfOutput = open(
                f"output/{date[3:5]}_{date[0:2]}_{nom.upper()}.pdf", 'wb')
            pdfWriter.write(pdfOutput)
            pdfOutput.close()
            self.canvas.itemconfigure(
                self.errorText, text="Pdf généré", fill="green")

        except Exception:
            self.canvas.itemconfigure(
                self.errorText, text="Erreur : chemin d'accès au pdf", fill="red")
            self.canvas.itemconfigure(
                self.pdfText, text="Document de location\nrempli par le locataire (.pdf) :", fill="red")
            return 0
