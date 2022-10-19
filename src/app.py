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

        self.root = Tk()
        self.root.title('Car PDF')
        self.root.tk.call('wm', 'iconphoto', self.root._w,
                          PhotoImage(file='ressources/logo_ceten.png'))

        self.root.geometry('700x350')
        self.root.resizable(0, 0)

        self.canvas = Canvas(self.root, width=700, height=350)
        self.canvas.pack(fill="both", expand=True)

        self.prenomEntry = Entry(self.root, width=50)
        self.nomEntry = Entry(self.root, width=50)
        self.dateEntry = Entry(self.root, width=50)
        self.kmEntry = Entry(self.root, width=50)
        self.pdfEntry = Button(
            self.root, text="Open Folder", command=getFilePath)

        # self.pdfEntry.pack(fill=X, padx=10)
        # self.pdfEntry.drop_target_register(DND_FILES)
        # self.pdfEntry.dnd_bind('<<Drop>>', self.DropPdf)

        self.prenomText = self.canvas.create_text(100, 50, text="Prénom")
        self.nomText = self.canvas.create_text(100, 100, text="Nom")
        self.dateText = self.canvas.create_text(100, 150, text="Date")
        self.kmText = self.canvas.create_text(100, 200, text="Km")
        self.pdfText = self.canvas.create_text(100, 250, text="Pdf")

        self.errorText = self.canvas.create_text(400, 330, text="")

        self.canvas.create_window(400, 50, window=self.prenomEntry)
        self.canvas.create_window(400, 100, window=self.nomEntry)
        self.canvas.create_window(400, 150, window=self.dateEntry)
        self.canvas.create_window(400, 200, window=self.kmEntry)
        self.canvas.create_window(400, 250, window=self.pdfEntry)

        self.button = Button(self.root, width=10,
                             command=self.CreatePDF, text="Remplir")
        self.button.bind("<Return>", self.CreatePDF)

        self.canvas.create_window(400, 300, window=self.button)

        self.root.mainloop()

    def CreatePDF(self, event=None):
        nom = self.nomEntry.get()
        prenom = self.prenomEntry.get()
        date = self.dateEntry.get()
        km = self.kmEntry.get()
        pdf = filePath

        if nom == "" or prenom == "" or date == "" or km == "" or pdf == "":
            self.canvas.itemconfigure(
                self.errorText, text="Erreur : champ vide", fill="red")
            return 0

        if not re.match(r"[0-9]{2}\/[0-9]{2}\/[0-9]{4}", date):
            self.canvas.itemconfigure(
                self.errorText, text="Erreur : format de la date", fill="red")
            return 0

        if not re.match(r"[1-9][0-9]*", km):
            self.canvas.itemconfigure(
                self.errorText, text="Erreur : format des km", fill="red")
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
            return 0
