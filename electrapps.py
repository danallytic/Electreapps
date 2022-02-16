from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QIcon, QImage, QKeySequence, QPalette,QBrush
from PyQt5.QtCore import Qt, QSize, QRect
import sys
import os
import numpy as np
import json as  jn
import electre1, electre2, electre3, electre4, electreis, electreiv, electretri

def resource_path(relative_path):
            """ Get absolute path to resource, works for dev and for PyInstaller """
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)
global image_dir, data_dir
image_dir = resource_path("images")
data_dir = resource_path("data")

global msg

def msg(self,message):
    Msg=QMessageBox(self)
    Msg.setIcon(QMessageBox.Warning)
    Msg.setText(message)
    Msg.show()

# implémentation des rapports sortie (rapport des resultats du calcule)
class doc_sortie(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(QRect(0,0, 1200, 650))
        self.sortie=QTextEdit(self)
        self.sortie.setGeometry(QRect(60, 80, 1050, 550))
        self.setStyleSheet("color:DarkBlue;font:Normal 16px")
        self.sortie.setStyleSheet("color:DarkBlue;font:Normal 16px")
        self.sortie.setReadOnly(True)
        self.setMinimumSize(900,500)
        self.saverapport=QAction("&Sauvegarer")
        self.saverapport.triggered.connect(self.save_report)
        self.menu=QMenuBar(self)
        self.menu.move(10,30)
        self.menu.resize(self.width()-20,30)
        self.menu.addAction(self.saverapport)
        self.closeEvent=self.close_table
    def save_report(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        if name!="":
            file = open(name,'w')
            contenu = self.sortie.toHtml()
            file.write(contenu)
            file.close()
        else:
            msg(self,"Le fichier n'a pas été sauvegardé")
    def close_table(self,event):
        if QMessageBox.question(self, 'Message', "Voulez-vous fermer le rapport?", QMessageBox.Ok, QMessageBox.Cancel)==QMessageBox.Ok:
            for action in self.parent().parent().parent().Fenetre_menu.actions():
                if action.text()==self.windowTitle():
                    self.parent().parent().parent().Fenetre_menu.removeAction(action)
            event.accept()
            self.deleteLater()
        else:
            event.ignore()
    def masquer_Action(self):
        self.hide()
    def afficher_Action(self):
        self.show()
# implémentation des tables projet (boite de dialogue pour parametrer le projet)
class n_table(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        self.path=sys.path
        # dictionnaire des variables locales 
        self.D_projet={
            "criteres":[],
            "choix":[],
            "nbchoix":0,
            "nbcriteres":0,
            "seuilconc":0.7,
            "seuilconc2":0.7,
            "seuilconc3":0.7,
            "seuildisc":0.5,
            "seuildisc2":0.5,
            "methode":0,
            "n_methode":"Electre I",
            "poids":[],
            "seuilsp":[],
            "seuilsq":[],
            "seuilsveto":[],
            "profils":[],
            "perf":[],
            "titre":"",
            "titresimple":"",
            "regle":"oc",
            "valid":[0,0,0]}
        self.choix_dic={}
        # contener des résultats
        self.resultats=()
        # formatage de la boite de dialogue projet
        self.setWindowTitle("liste des choix et des critères")
        self.setMinimumSize(900,500)
        self.setStyleSheet("color:DarkBlue;font:Normal 16px")
        # table des performances
        self.table_performances=QTableWidget(self)
        self.table_performances.setVisible(False)
        self.table_performances.setGeometry(QRect(60, 80, 1050, 550))
        self.label_tableperf=QLabel(self)
        self.label_tableperf.setText("Table des performances")
        self.label_tableperf.setGeometry(QRect(390, 40, 300, 21))
        self.label_tableperf.setVisible(False)
        self.afficher_param=QPushButton(self)
        self.afficher_param.setText("Paramètres")
        self.afficher_param.setGeometry(QRect(1130,80,120,40))
        self.afficher_param.setVisible(False)
        self.afficher_param.clicked.connect(self.affich_param)
        self.valider_perf=QPushButton(self)
        self.valider_perf.setText("Valider")
        self.valider_perf.setGeometry(QRect(1130,130,120,40))       
        self.valider_perf.setVisible(False)
        self.valider_perf.clicked.connect(self.valid_perf)
        # paneau de configuration des paramettres
        self.Projrt_Parametres = QTabWidget(self)
        self.Projrt_Parametres.setGeometry(QRect(60, 70, 700, 350))
        self.Projrt_Parametres.setObjectName("Projrt_Parametres")
        # volet des données globale sur le projet
        self.Projet = QWidget()
        self.Projet.setObjectName("Projet")
        self.label_titre = QLabel(self.Projet)
        self.label_titre.setGeometry(QRect(80, 20, 180, 21))
        self.label_titre.setObjectName("label_titre")
        self.label_titre.setText( "Titre du projet")
        self.edit_titre = QLineEdit(self.Projet)
        self.edit_titre.setGeometry(QRect(200, 15, 300, 30))
        self.edit_titre.setObjectName("edit_titre")
        self.label_nbchoix = QLabel(self.Projet)
        self.label_nbchoix.setGeometry(QRect(240, 80, 150, 20))
        self.label_nbchoix.setObjectName("label_nbchoix")
        self.label_nbchoix.setText( "Nombre de Choix")
        self.label_nbcriters = QLabel(self.Projet)
        self.label_nbcriters.setGeometry(QRect(240, 120, 150, 16))
        self.label_nbcriters.setObjectName("label_nbcriters")
        self.label_nbcriters.setText( "Nombre de critères")
        self.label_sconcordance = QLabel(self.Projet)
        self.label_sconcordance.setGeometry(QRect(240, 160, 150, 16))
        self.label_sconcordance.setObjectName("label_sconcordance")
        self.label_sconcordance.setText( "Seuil de concordance")
        self.label_sdiscordance = QLabel(self.Projet)
        self.label_sdiscordance.setGeometry(QRect(240, 200, 150, 16))
        self.label_sdiscordance.setObjectName("label_sdiscordance")
        self.label_sdiscordance.setText( "Seuil de discordance")
        # nombre des alternatives
        self.nbchoix = QSpinBox(self.Projet)
        self.nbchoix.setGeometry(QRect(450, 80, 111, 22))
        self.nbchoix.setObjectName("nbchoix")
        self.nbchoix.setMinimum(2)
        # nombre de critères
        self.nbcriteres = QSpinBox(self.Projet)
        self.nbcriteres.setGeometry(QRect(450, 120, 111, 22))
        self.nbcriteres.setObjectName("nbcriteres")
        self.nbcriteres.setMinimum(2)
        #  seuils
        self.seuilconc = QDoubleSpinBox(self.Projet)
        self.seuilconc.setGeometry(QRect(450, 160, 55, 22))
        self.seuilconc.setObjectName("seuilconc")
        self.seuilconc.setRange(0,1)
        self.seuilconc.setSingleStep(0.05)
        self.seuilconc.setValue(0.70)
        self.seuilconc2 = QDoubleSpinBox(self.Projet)
        self.seuilconc2.setGeometry(QRect(510, 160, 55, 22))
        self.seuilconc2.setRange(0,1)
        self.seuilconc2.setSingleStep(0.05)
        self.seuilconc2.setValue(0.70)
        self.seuilconc2.setVisible(False)
        self.seuilconc3 = QDoubleSpinBox(self.Projet)
        self.seuilconc3.setGeometry(QRect(570, 160, 55, 22))
        self.seuilconc3.setRange(0,1)
        self.seuilconc3.setSingleStep(0.05)
        self.seuilconc3.setValue(0.70)
        self.seuilconc3.setVisible(False)
        self.seuildisc = QDoubleSpinBox(self.Projet)
        self.seuildisc.setGeometry(QRect(450, 200, 55, 22))
        self.seuildisc.setObjectName("seuildisc")
        self.seuildisc.setRange(0,1)
        self.seuildisc.setSingleStep(0.05)
        self.seuildisc.setValue(0.50)
        self.seuildisc2 = QDoubleSpinBox(self.Projet)
        self.seuildisc2.setGeometry(QRect(510, 200, 55, 22))
        self.seuildisc2.setRange(0,1)
        self.seuildisc2.setSingleStep(0.05)
        self.seuildisc2.setValue(0.50)
        self.seuildisc2.setVisible(False)
        # cadre type de méthodes electre
        self.frame = QFrame(self.Projet)
        self.frame.setGeometry(QRect(30, 80, 145, 180))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Sunken)
        # les methodes electre
        self.electr_i = QRadioButton(self.frame)
        self.electr_i.setGeometry(QRect(13, 30, 100, 17))
        self.electr_i.setObjectName("electr_i")
        self.electr_i.setText( "Electre I")
        self.electr_i.setChecked(True)
        self.electr_i.toggled.connect(self.elec)
        self.electr_is = QRadioButton(self.frame)
        self.electr_is.setGeometry(QRect(13, 50, 100, 17))
        self.electr_is.setObjectName("electr_is")
        self.electr_is.setText( "Electre i-S")
        self.electr_is.toggled.connect(self.elec)
        self.electr_iv = QRadioButton(self.frame)
        self.electr_iv.setGeometry(QRect(13, 70, 100, 17))
        self.electr_iv.setObjectName("electr_iv")
        self.electr_iv.setText( "Electre i-V")
        self.electr_iv.toggled.connect(self.elec)
        self.electr_ii = QRadioButton(self.frame)
        self.electr_ii.setGeometry(QRect(13, 90, 100, 17))
        self.electr_ii.setObjectName("electr_ii")
        self.electr_ii.setText( "Electre II")
        self.electr_ii.toggled.connect(self.elec)
        self.electr_iii = QRadioButton(self.frame)
        self.electr_iii.setGeometry(QRect(13, 110, 100, 17))
        self.electr_iii.setObjectName("electr_iii")
        self.electr_iii.setText( "Electre III")
        self.electr_iii.toggled.connect(self.elec)
        self.electr_4 = QRadioButton(self.frame)
        self.electr_4.setGeometry(QRect(13, 130, 100, 17))
        self.electr_4.setObjectName("electr_4")
        self.electr_4.setText( "Electre IV")
        self.electr_4.toggled.connect(self.elec)
        self.electr_tri = QRadioButton(self.frame)
        self.electr_tri.setGeometry(QRect(13, 150, 100, 17))
        self.electr_tri.setObjectName("electr_tri")
        self.electr_tri.setText( "Electre TRI")
        self.electr_tri.toggled.connect(self.elec)
        self.method_analyse = QLabel(self.frame)
        self.method_analyse.setGeometry(QRect(10, 10, 160, 16))
        self.method_analyse.setObjectName("method_analyse")
        self.method_analyse.setText( "Methode d\'analyse")
        self.mode_etri=QComboBox(self.Projet)
        self.mode_etri.setGeometry(QRect(30, 261, 145, 26))
        self.mode_etri.addItem("Règle Optimiste")
        self.mode_etri.addItem("Règle Pescimiste")
        self.mode_etri.setVisible(False)
        self.mode_etri.currentIndexChanged.connect(self.select_mode)
        # les boutons du premier volet
        self.reitialise_proj = QPushButton(self.Projet)
        self.reitialise_proj.setGeometry(QRect(420, 280, 121, 26))
        self.reitialise_proj.setObjectName("reitialise_proj")
        self.reitialise_proj.setText( "Editer")
        self.reitialise_proj.clicked.connect(self.reinitiatise_projet)
        self.valider_proj = QPushButton(self.Projet)
        self.valider_proj.setGeometry(QRect(560, 280, 111, 26))
        self.valider_proj.setObjectName("valider_proj")
        self.valider_proj.setText("Valider")
        self.valider_proj.clicked.connect(self.valide_proj)
        self.Projrt_Parametres.addTab(self.Projet, "")
        self.Projrt_Parametres.setTabText(self.Projrt_Parametres.indexOf(self.Projet),  "Parametrage du Projet")
        # table des noms des choix et critères
        self.tab_noms = QWidget()
        self.tab_noms.setObjectName("tab_noms")
        self.tab_noms.setEnabled(False)
        # entrée d'une alternative
        self.choix = QLineEdit(self.tab_noms)
        self.choix.setGeometry(QRect(30, 37, 270, 31))
        self.choix.setObjectName("choix")
        self.choix.returnPressed.connect(self.add_to_choix)
        # entrée d'un critère
        self.criters = QLineEdit(self.tab_noms)
        self.criters.setGeometry(QRect(350, 37, 270, 31))
        self.criters.setObjectName("criters")
        self.criters.returnPressed.connect(self.add_to_criteres)
        # liste des alternatives
        self.liste_choix = QListWidget(self.tab_noms)
        self.liste_choix.setGeometry(QRect(30, 71, 270, 210))
        self.liste_choix.setObjectName("liste_choix")
        self.liste_choix.keyPressEvent=self.delchoix
        self.liste_choix.doubleClicked.connect(self.edit_choix)
        self.liste_choix.itemChanged.connect(self.delete_choix)
        # liste des critères
        self.liste_criteres = QListWidget(self.tab_noms)
        self.liste_criteres.setGeometry(QRect(350, 71, 270, 210))
        self.liste_criteres.setObjectName("liste_criteres")
        self.liste_criteres.keyPressEvent=self.delcritere
        self.liste_criteres.doubleClicked.connect(self.edit_critere)
        self.liste_criteres.itemChanged.connect(self.delete_critere)
        # les boutons du deuxième volet
        self.vider_choix = QPushButton(self.tab_noms)
        self.vider_choix.setGeometry(QRect(105, 290, 100, 23))
        self.vider_choix.setObjectName("vider_choix")
        self.vider_choix.setText( "Vider la liste")
        self.vider_choix.clicked.connect(self.vide_choix)
        self.vider_criteres = QPushButton(self.tab_noms)
        self.vider_criteres.setGeometry(QRect(425, 290, 100, 23))
        self.vider_criteres.setObjectName("vider_criteres")
        self.vider_criteres.setText( "Vider la liste")
        self.vider_criteres.clicked.connect(self.vide_criteres)
        self.noms_auto= QPushButton(self.tab_noms)
        self.noms_auto.setGeometry(QRect(265, 290, 100, 23))
        self.noms_auto.setObjectName("nom_auto")
        self.noms_auto.setText( "noms auto")
        self.noms_auto.clicked.connect(self.nomer_auto)
        self.valider_criteres = QPushButton(self.tab_noms)
        self.valider_criteres.setGeometry(QRect(600, 290, 90, 23))
        self.valider_criteres.setObjectName("valider_criteres")
        self.valider_criteres.setText( "Valider")
        self.valider_criteres.clicked.connect(self.valide_criteres)
        # les titres du deuxième volet
        self.labels_choix = QLabel(self.tab_noms)
        self.labels_choix.setGeometry(QRect(40, 10, 161, 21))
        self.labels_choix.setObjectName("labels_choix")
        self.labels_choix.setText( "Labèles des choix ")
        self.labels_criteres = QLabel(self.tab_noms)
        self.labels_criteres.setGeometry(QRect(360, 10, 161, 21))
        self.labels_criteres.setObjectName("labels_criteres")
        self.labels_criteres.setText( "Labèles des critères")
        self.Projrt_Parametres.addTab(self.tab_noms, "")
        self.Projrt_Parametres.setTabText(self.Projrt_Parametres.indexOf(self.tab_noms),  "listes des choix et critères")
        # table des poids et seuils
        self.tab_poids = QWidget()
        self.tab_poids.setObjectName("tab_poids")
        self.tab_poids.setEnabled(False)
        self.table_poids = QTableWidget(self.tab_poids)
        self.table_poids.setGeometry(QRect(10, 60, 666, 200))
        self.table_poids.setObjectName("table_poids")
        self.table_poids.setColumnCount(0)
        self.table_poids.setRowCount(1)
        item = QTableWidgetItem()
        self.table_poids.setVerticalHeaderItem(0, item)
        item = self.table_poids.verticalHeaderItem(0)
        item.setText( "Poids")
        # titres du troisième volet
        self.label_poids = QLabel(self.tab_poids)
        self.label_poids.setGeometry(QRect(20, 20, 200, 21))
        self.label_poids.setObjectName("label_poids")
        self.label_poids.setText( "Caractérisation des critères")
        # les boutons du troisième volet
        self.valider_poids = QPushButton(self.tab_poids)
        self.valider_poids.setGeometry(QRect(420, 280, 111, 31))
        self.valider_poids.setText( "Valider")
        self.valider_poids.setObjectName("valider_poids")
        self.valider_poids.clicked.connect(self.valide_poids)
        self.fermer_param = QPushButton(self.tab_poids)
        self.fermer_param.setGeometry(QRect(560, 280, 105, 31))
        self.fermer_param.setObjectName("fermer_param")
        self.fermer_param.setText( "Performances")
        self.fermer_param.setEnabled(False)
        self.fermer_param.clicked.connect(self.ferme_param)
        self.Projrt_Parametres.addTab(self.tab_poids, "")
        self.Projrt_Parametres.setTabText(self.Projrt_Parametres.indexOf(self.tab_poids),  "Parametrage des critères")
        self.table_poids.itemChanged.connect(self.table_changed)
        self.Projrt_Parametres.setCurrentIndex(0)
        # le menu de la table projet
        self.closeEvent=self.close_table 
        self.save=QAction("&Enregistrer",self)
        self.save.triggered.connect(self.save_project)
        self.open=QAction("&Ouvrir")
        self.open.triggered.connect(self.open_project)
        self.calcul=QAction("&Calcule")
        self.calcul.triggered.connect(self.calcule)
        self.sortie=QAction("&Résultat")
        self.sortie.triggered.connect(self.sortie_resultats)
        self.menu=QMenuBar(self)
        self.menu.move(10,30)
        self.menu.resize(self.width()-20,30)
        self.menu.addAction(self.save)
        self.menu.addAction(self.open)
        self.menu.addAction(self.calcul)
        self.menu.addAction(self.sortie)
        self.menu.show()
        self.resizeEvent=self.adapt_menu
        
    # adapter le menu à la fenêtre
    def adapt_menu(self,event):
        super().resizeEvent(event)
        if not self.isMaximized():
            self.menu.move(10,30)
            self.menu.resize(self.width()-20,30)
        else:
            self.menu.move(0,0)
            self.menu.resize(self.width(),30)
    # selection des paramètres correspondant a chaque méthode
    def elec(self):
        electre=self.sender()
        self.D_projet["n_methode"]=electre.text()
        if electre.text()=="Electre TRI" or electre.text()=="Electre i-S": 
            self.label_sconcordance.setText("Paramètre Lambda")
        else:
            self.label_sconcordance.setText("Seuil de concordance")
        if electre.text()=="Electre TRI": 
            self.mode_etri.setVisible(True)
        else:
            self.mode_etri.setVisible(False)
        if electre.text()=="Electre II":
            self.seuilconc.setVisible(True)
            self.label_sconcordance.setVisible(True)
            self.seuilconc2.setVisible(True)
            self.seuilconc3.setVisible(True)
            self.seuildisc2.setVisible(True)
            self.seuildisc.setVisible(True)
            self.label_sdiscordance.setVisible(True)
            self.seuilconc.setValue(0.7)
            self.seuildisc.setValue(0.5)
        elif electre.text()=="Electre I":
            self.seuilconc2.setVisible(False)
            self.seuilconc3.setVisible(False)
            self.seuildisc2.setVisible(False)
            self.seuildisc.setVisible(True)
            self.label_sdiscordance.setVisible(True)
            self.seuilconc.setVisible(True)
            self.label_sconcordance.setVisible(True)
            self.seuilconc.setValue(0.7)
            self.seuildisc.setValue(0.5)
        elif electre.text()=="Electre i-V" or electre.text()=="Electre TRI" or electre.text()=="Electre i-S" :
            self.seuilconc2.setVisible(False)
            self.seuilconc3.setVisible(False)
            self.seuildisc2.setVisible(False)
            self.seuildisc.setVisible(False)
            self.label_sdiscordance.setVisible(False)
            self.seuilconc.setVisible(True)
            self.label_sconcordance.setVisible(True)
            self.seuilconc.setValue(0.7)
            self.seuildisc.setValue(0.5)
        else:
            self.seuilconc2.setVisible(False)
            self.seuilconc3.setVisible(False)
            self.seuildisc2.setVisible(False)
            self.seuildisc.setVisible(False)
            self.label_sdiscordance.setVisible(False)
            self.seuilconc.setVisible(False)
            self.label_sconcordance.setVisible(False)
            self.seuilconc.setValue(0.7)
            self.seuilconc2.setValue(0.7)
            self.seuilconc3.setValue(0.7)
            self.seuildisc.setValue(0.5)
            self.seuildisc2.setValue(0.5)
    # selectionner la règle de calcule pour la méthode electre tri (optimiste ou péscimiste)
    def select_mode(self,i):
        if i==0: 
            self.D_projet["regle"]="oc"
        else:
            self.D_projet["regle"]="pc"
    # fermeture d'une table
    def close_table(self,event):
        if QMessageBox.question(self, 'Message', "Voulez-vous abandonner le projet?", QMessageBox.Ok, QMessageBox.Cancel)==QMessageBox.Ok:
            for action in self.parent().parent().parent().Fenetre_menu.actions():
                if action.text()==self.windowTitle():
                    self.parent().parent().parent().Fenetre_menu.removeAction(action)
            event.accept()
            self.deleteLater()
        else:
            event.ignore()
    def masquer_Action(self):
        self.hide()
    def afficher_Action(self):
        self.show()
    # aajouter une alternative
    def add_to_choix(self):
        if self.choix.text()!= "" and self.liste_choix.count()<self.D_projet["nbchoix"]:
            self.liste_choix.addItem(self.choix.text())
        self.choix.setText("")
    # ajouter un critère
    def add_to_criteres(self):
        if self.criters.text()!= "" and self.liste_criteres.count()<self.D_projet["nbcriteres"]:
            self.liste_criteres.addItem(self.criters.text())
        self.criters.setText("")
    # valider le projet
    def valide_proj(self):
        if self.edit_titre.text().strip()!="" and self.nbchoix.value()!=0 and self.nbcriteres.value()!=0 and self.seuilconc.value()*self.seuilconc2.value()*self.seuilconc3.value()*self.seuildisc.value()*self.seuildisc2.value()!=0:
            if self.electr_ii.isChecked() and not(self.seuilconc.value()<self.seuilconc2.value() and self.seuilconc2.value()<self.seuilconc3.value() and self.seuildisc.value()<self.seuildisc2.value()):
                msg(self,"les seuils de concordance ainsi que de discordance doivent être strictement croissants!")
                return
            self.D_projet["methode"]=1*self.electr_i.isChecked()+2*self.electr_is.isChecked()+3*self.electr_iv.isChecked()+4*self.electr_ii.isChecked()+5*self.electr_iii.isChecked()+6*self.electr_4.isChecked()+7*self.electr_tri.isChecked()
            self.D_projet["titre"]=self.edit_titre.text()+" "+"("+self.D_projet["n_methode"]+")"
            self.D_projet["nbchoix"]=self.nbchoix.value()
            self.D_projet["nbcriteres"]=self.nbcriteres.value()
            self.D_projet["seuilconc"]=self.seuilconc.value()
            self.D_projet["seuilconc2"]=self.seuilconc2.value()
            self.D_projet["seuilconc3"]=self.seuilconc3.value()
            self.D_projet["seuildisc"]=self.seuildisc.value()
            self.D_projet["seuildisc2"]=self.seuildisc2.value()
            self.Projrt_Parametres.setCurrentIndex(1)
            self.tab_noms.setEnabled(True)
            self.choix.setEnabled(True)
            self.criters.setEnabled(True)
            composants=self.Projet.children()
            for composant in composants:
                composant.setEnabled(False)
            self.reitialise_proj.setEnabled(True)
            # self.setWindowTitle(self.D_projet["titre"])
            
            self.D_projet["valid"][0]=1
        else:
            msg(self,"Complettez les données avant de valider!")
            
    # valider les labèles des critères et des alternatives
    def valide_criteres(self):
        if self.liste_choix.count()==self.D_projet["nbchoix"] and self.liste_criteres.count()==self.D_projet["nbcriteres"] and self.D_projet["nbchoix"]*self.D_projet["nbcriteres"]!=0:
            self.table_poids.setColumnCount(self.liste_criteres.count())
            self.D_projet["criteres"]=[]
            for i in range(self.liste_criteres.count()):
                self.D_projet["criteres"].append(self.liste_criteres.item(i).text())
                self.table_poids.setHorizontalHeaderItem(i, QTableWidgetItem(self.liste_criteres.item(i).text()))
            self.D_projet["choix"]=[]
            for i in range(self.liste_choix.count()):
                self.D_projet["choix"].append(self.liste_choix.item(i).text())
                self.choix_dic["a"+str(i+1)]=self.D_projet["choix"][i]
                #------------------------------------------------------------
            self.Projrt_Parametres.setCurrentIndex(2)
            if self.D_projet["methode"]==1 or self.D_projet["methode"]==4 :
                self.table_poids.setRowCount(1)
            elif self.D_projet["methode"]==3:
                self.table_poids.setRowCount(2)
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(1, item)
                item = self.table_poids.verticalHeaderItem(1)
                item.setText("Seuil de Veto")
            elif self.D_projet["methode"]==6:
                self.table_poids.setRowCount(3)
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(1, item)
                item = self.table_poids.verticalHeaderItem(1)
                item.setText( "Seuil p")
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(2, item)
                item = self.table_poids.verticalHeaderItem(2)
                item.setText("Seuil de Veto")
                
            else:
                self.table_poids.setRowCount(4)
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(1, item)
                item = self.table_poids.verticalHeaderItem(1)
                item.setText( "Seuil q")
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(2, item)
                item = self.table_poids.verticalHeaderItem(2)
                item.setText( "Seuil p")
                item = QTableWidgetItem()
                self.table_poids.setVerticalHeaderItem(3, item)
                item = self.table_poids.verticalHeaderItem(3)
                item.setText("Seuil de Veto")
                
            self.D_projet["valid"][1]=1
            self.choix.setEnabled(False)
            self.criters.setEnabled(False)
            self.tab_poids.setEnabled(True)
            self.valider_poids.setEnabled(True)
            self.table_performances.setRowCount(self.D_projet["nbchoix"])
            self.table_performances.setColumnCount(self.D_projet["nbcriteres"]+1)
            entetes=self.D_projet["criteres"][:]
            entetes.append("Profiles")
            self.table_performances.setHorizontalHeaderLabels(entetes)
            self.table_performances.setVerticalHeaderLabels(self.D_projet["choix"])
        else:
            msg(self,"Verifier les nombres des choix et des critères avant de valider!\n"+" Nombre de choix="+str(self.D_projet["nbchoix"])+" et nombre de critères="+str(self.D_projet["nbcriteres"]))
    # éditer un labèle d'alternative
    def edit_choix(self):
        index = self.liste_choix.currentIndex()
        if index.isValid():
            item = self.liste_choix.itemFromIndex(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        if not item.isSelected():
            item.setSelected(True)
        self.liste_choix.edit(index)
    # éditer un labèle de critère
    def edit_critere(self):
        index = self.liste_criteres.currentIndex()
        if index.isValid():
            item = self.liste_criteres.itemFromIndex(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        if not item.isSelected():
            item.setSelected(True)
        self.liste_criteres.edit(index)
    # supprimer une alternative vide
    def delete_choix(self):
        index = self.liste_choix.currentIndex()
        if index.isValid():
            item = self.liste_choix.itemFromIndex(index)
        if item.text()=="":
            self.liste_choix.takeItem(index.row())
    # supprimer un critère vide
    def delete_critere(self):
        index = self.liste_criteres.currentIndex()
        if index.isValid():
            item = self.liste_criteres.itemFromIndex(index)
        if item.text()=="":
            self.liste_criteres.takeItem(index.row())
    # effacer une alternative par touche supr ou backspace
    def delchoix(self,e):
        if e.key()==16777219 or e.key()==16777223:
            index = self.liste_choix.currentIndex()
            self.liste_choix.takeItem(index.row())
    # effacer un crtère par touche supr ou backspace
    def delcritere(self,e):
        if e.key()==16777219 or e.key()==16777223:
            index = self.liste_criteres.currentIndex()
            self.liste_criteres.takeItem(index.row())
    # detecte un changement dans les paramétres du projet
    def table_changed(self):
        self.D_projet["valid"][2]=0
        self.fermer_param.setEnabled(False)
    # valider les poids et les differents seuils
    def valide_poids(self):
        if self.D_projet["valid"][2]==0:
            if self.D_projet["methode"] in [2,5,7]:
                for column in range(self.table_poids.columnCount()):
                    item = self.table_poids.item(3, column)
                    if float(item.text())<0 or float(item.text())>1:
                        msg(self,"les seuils de veto doivent être compris entre 0 et 1")
                        return
            if self.D_projet["methode"] == 6:
                for column in range(self.table_poids.columnCount()):
                    item = self.table_poids.item(2, column)
                    if float(item.text())<0 or float(item.text())>1:
                        msg(self,"les seuils de veto doivent être compris entre 0 et 1")
                        return
            if self.D_projet["methode"] == 3:
                for column in range(self.table_poids.columnCount()):
                    item = self.table_poids.item(1, column)
                    if float(item.text())<0 or float(item.text())>1:
                        msg(self,"les seuils de veto doivent être compris entre 0 et 1")
                        return
            if self.D_projet["methode"] == 6:
                for column in range(self.table_poids.columnCount()):
                    item = self.table_poids.item(1, column)
                    if float(item.text())<0 or float(item.text())>1:
                        msg(self,"les seuils p doivent être compris entre 0 et 1")
                        return
            try:
                self.D_projet["poids"],self.D_projet["seuilsp"],self.D_projet["seuilsq"],self.D_projet["seuilsveto"]=[],[],[],[]
                if self.D_projet["methode"]!=6:
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(0, column)
                        self.D_projet["poids"].append(float(item.text()))
                if self.D_projet["methode"]==3:
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(1, column)
                        self.D_projet["seuilsveto"].append(float(item.text()))
                if self.D_projet["methode"] in [2,5,7]:
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(1, column)
                        item2 = self.table_poids.item(2, column)
                        if 1 > float(item.text()) and float(item.text()) > float(item2.text()):
                            self.D_projet["seuilsq"].append(float(item.text()))
                            self.D_projet["seuilsp"].append(float(item2.text()))
                        else:
                            msg(self,"les seuils p doivent être inferieurs aux seuils q et compris entre 0 et 1")
                            return
                    
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(3, column)
                        self.D_projet["seuilsveto"].append(float(item.text()))
                if self.D_projet["methode"]==6:
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(0, column)
                        self.D_projet["seuilsp"].append(float(item.text()))
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(1, column)
                        self.D_projet["seuilsq"].append(float(item.text()))
                    for column in range(self.table_poids.columnCount()):
                        item = self.table_poids.item(2, column)
                        self.D_projet["seuilsveto"].append(float(item.text()))

                self.D_projet["valid"][2]=1
                self.fermer_param.setEnabled(True)
                self.fermer_param.setStyleSheet("background-color: lightgreen;")
            except:
                self.D_projet["poids"],self.D_projet["seuilsp"],self.D_projet["seuilsq"],self.D_projet["seuilsveto"]=[],[],[],[]
                msg(self,"Complettez correctement les données avant de valider!")

    # valider les performances des alternatives
    def valid_perf(self):
        try:
            self.D_projet["perf"]=[]
            self.D_projet["profils"]=[]
            for i in range(self.table_performances.rowCount()):
                ligne=[]
                for j in range(self.table_performances.columnCount()-1):
                    item=self.table_performances.item(i,j).text()
                    ligne.append(float(item))
                self.D_projet["perf"].append(ligne)
                j=self.table_performances.columnCount()-1
                item=self.table_performances.item(i,j).text()
                if int(item) == 0 or int(item) == 1:
                    if int(item) == 1:
                        lignep=[]
                        lignep=ligne[:]
                        lignep.append(i)
                        self.D_projet["profils"].append(lignep)
                else:
                    msg(self,"Les profiles choisis prennent la valeur (1) les autres (0)")
                    return
            print(self.D_projet["profils"])
            self.D_projet["titresimple"]=self.D_projet["titre"].replace(" ", "")
        except:
            self.D_projet["perf"]=[]
            msg(self,"Complettez correctement les données avant de valider!")

    # permet l'edition du projet pour changer ses paramétres
    def reinitiatise_projet(self):
        composants=self.Projet.children()
        for composant in composants:
            composant.setEnabled(True)
        self.valider_proj.setEnabled(True)
        self.tab_noms.setEnabled(False)
        self.tab_poids.setEnabled(False)
        self.fermer_param.setStyleSheet("background-color: lightgray;")
        self.D_projet["valid"]=[0,0,0]
    # vider la liste des alternatives
    def vide_choix(self):
        self.liste_choix.clear()
        self.D_projet["choix"]=[]
        self.D_projet["valid"][1]=0
    # vider la liste des critères
    def vide_criteres(self):
        self.liste_criteres.clear()
        self.D_projet["criteres"]=[]
        self.D_projet["valid"][1]=0
    # générer automatiquement des labèles des alternatives et des critères
    def nomer_auto(self):
        self.liste_criteres.clear()
        self.liste_choix.clear()
        for i in range(self.D_projet["nbchoix"]):
            item=QListWidgetItem()
            item.setText("Alternative "+str(i+1))
            self.liste_choix.addItem(item)
            
        for j in range(self.D_projet["nbcriteres"]):
            item=QListWidgetItem()
            item.setText("Critère "+str(j+1))
            self.liste_criteres.addItem(item)
    # fermer la table des paramétres d'un projet
    def ferme_param(self):
        if not(0 in self.D_projet["valid"]):
            self.Projrt_Parametres.setVisible(False)
            self.table_performances.setVisible(True)
            self.label_tableperf.setVisible(True)
            self.afficher_param.setVisible(True)
            self.valider_perf.setVisible(True)
            self.afficher_param.setText("Paramètres")
            self.showMaximized()
            self.menu.move(0,0)
            self.menu.resize(self.width(),30)
            self.setMinimumSize(1275,650)
        else:
            msg(self,"Complettez les données avant de fermer la table des parametres!")

    # afficher les paramétres d'un projet
    def affich_param(self):
        if self.afficher_param.text()=="Paramètres":
            self.Projrt_Parametres.setVisible(True)
            self.table_performances.setVisible(False)
            self.label_tableperf.setVisible(False)
            self.valider_perf.setVisible(False)
            self.afficher_param.setText("Performances")
            self.fermer_param.setEnabled(False)
            self.fermer_param.setStyleSheet("background-color: lightgray;")
        else:
            if self.D_projet["valid"]==[1,1,1]:
                self.Projrt_Parametres.setVisible(False)
                self.table_performances.setVisible(True)
                self.label_tableperf.setVisible(True)
                self.valider_perf.setVisible(True)
                self.afficher_param.setText("Paramètres")
            else:
                msg(self,"Validez d'abord vos changements!")

    # enregistrer un projet
    def save_project(self):
        try:
            fichierdlg =QFileDialog.getSaveFileName(
                parent=self,
                caption='Enregistrer un fichier',
                directory=data_dir + self.D_projet["titre"]+" "+self.D_projet["n_methode"]+".elec" ,
                # directory=self.path[0]+"/data/"+self.D_projet["titre"]+" "+self.D_projet["n_methode"]+".elec" ,
                filter='Fichiers Electre (*.elec)',

            )
            nfichier=fichierdlg[0]
            if nfichier!="":
                fichier= open(nfichier,"w")
                jn.dump(self.D_projet,fichier)
                fichier.close()
            else:
                msg(self,"L'enregistrement a été annulé")

        except:
            msg(self,"L'enregistrement a été abandonné suite à une erreur système")
            
    # ouvrir un projet sauvegardé sur le disque
    def open_project(self):
        try:
            fichierdlg =QFileDialog.getOpenFileName(
                parent=self,
                caption='Ouvrir un fichier',
                directory=data_dir,
                # directory=self.path[0]+"/data/",
                filter='Fichiers Electre (*.elec)',
            )
            nfichier=fichierdlg[0]
            if nfichier=="":
                for action in self.parent().parent().parent().Fenetre_menu.actions():
                    if action.text()==self.windowTitle():
                        self.parent().parent().parent().Fenetre_menu.removeAction(action)
                self.deleteLater()
                ok=False 
                return ok
            else:
                fichier = open(nfichier, "r")
                self.D_projet = jn.load(fichier)
                if "regle" not in self.D_projet.keys() : self.D_projet["regle"]="oc"
                # chargement des données dans le panneau de paramétrage
                if self.D_projet["methode"]==1:
                    self.electr_i.setChecked(True)
                elif self.D_projet["methode"]==2:
                    self.electr_is.setChecked(True)
                elif self.D_projet["methode"]==3:
                    self.electr_iv.setChecked(True)
                elif self.D_projet["methode"]==4:
                    self.electr_ii.setChecked(True)
                elif self.D_projet["methode"]==5:
                    self.electr_iii.setChecked(True)
                elif self.D_projet["methode"]==6:
                    self.electr_4.setChecked(True)
                else:
                    self.electr_tri.setChecked(True)
                    
                    if self.D_projet["regle"]=="oc":
                        self.mode_etri.setCurrentIndex(0)
                    else:
                        self.mode_etri.setCurrentIndex(1)
                #self.Projet.setEnabled(False)
                self.edit_titre.setText(self.D_projet["titre"])
                self.nbchoix.setValue(self.D_projet["nbchoix"])
                self.nbcriteres.setValue(self.D_projet["nbcriteres"])
                self.seuilconc.setValue(self.D_projet["seuilconc"])
                self.seuilconc2.setValue(self.D_projet["seuilconc2"])
                self.seuilconc3.setValue(self.D_projet["seuilconc3"])
                self.seuildisc.setValue(self.D_projet["seuildisc"])
                self.seuildisc2.setValue(self.D_projet["seuildisc2"])
                
                self.liste_choix.addItems(self.D_projet["choix"])
                self.liste_criteres.addItems(self.D_projet["criteres"])
                self.valide_criteres()

                if self.D_projet["methode"]!=6:
                    for column in range(self.table_poids.columnCount()):
                        item=QTableWidgetItem(str(self.D_projet["poids"][column]))
                        self.table_poids.setItem(0, column, item)    
                
                if self.D_projet["methode"]==3:
                    for column in range(self.table_poids.columnCount()):
                        item=QTableWidgetItem(str(self.D_projet["seuilsveto"][column]))
                        item = self.table_poids.setItem(1, column, item)
                        
                if self.D_projet["methode"] in [2,5,7]:
                    for column in range(self.table_poids.columnCount()):
                        item=QTableWidgetItem(str(self.D_projet["seuilsp"][column]))
                        self.table_poids.setItem(1, column, item)
                        
                    for column in range(self.table_poids.columnCount()):
                        item = item=QTableWidgetItem(str(self.D_projet["seuilsq"][column]))
                        self.table_poids.setItem(2, column,item)
                        
                    for column in range(self.table_poids.columnCount()):
                        item = item=QTableWidgetItem(str(self.D_projet["seuilsveto"][column]))
                        self.table_poids.setItem(3, column, item)
                        
                if self.D_projet["methode"]==6:
                    for column in range(self.table_poids.columnCount()):
                        item = item=QTableWidgetItem(str(self.D_projet["seuilsp"][column])) 
                        self.table_poids.setItem(0, column, item)
                        
                    for column in range(self.table_poids.columnCount()):
                        item = item=QTableWidgetItem(str(self.D_projet["seuilsq"][column]))
                        self.table_poids.setItem(1, column, item)
                        
                    for column in range(self.table_poids.columnCount()):
                        item = item=QTableWidgetItem(str(self.D_projet["seuilsveto"][column]))
                        self.table_poids.setItem(2, column, item)
                        
                for i in range(self.table_performances.rowCount()):
                    ligne=self.D_projet["perf"][i]
                    for j in range(self.table_performances.columnCount()-1):
                        item=QTableWidgetItem(str(ligne[j]))
                        self.table_performances.setItem(i,j,item)
                    j=self.table_performances.columnCount()-1
                    ligne=ligne+[i]
                    if ligne in self.D_projet["profils"]:
                        item=QTableWidgetItem(str(1))
                        self.table_performances.setItem(i,j,item)
                    else:
                        item=QTableWidgetItem(str(0))
                        self.table_performances.setItem(i,j,item)
                    ligne=[]
                    
                self.valider_poids.setEnabled(False)
                self.fermer_param.setEnabled(True)
                self.valider_perf.setEnabled(True)
                self.Projrt_Parametres.setCurrentIndex(0)
                self.D_projet["valid"]=[1,1,1]
                self.show()
                self.valide_proj
                ok=True
                return ok
        except:
            for action in self.parent().parent().parent().Fenetre_menu.actions():
                if action.text()==self.windowTitle():
                    self.parent().parent().parent().Fenetre_menu.removeAction(action)
            msg=QMessageBox(self.parent().parent().parent())
            msg.setIcon(QMessageBox.Warning)
            msg.setText("le fichier n'a pas pu être entierement chargé")
            msg.show()
            self.deleteLater()
            ok=False
            return ok
    # générer le rapport des résultats d'un projet
    def sortie_resultats(self):
        if self.resultats!=():
            window.sortieAction(self)
    # calculer les résultats d'un projet
    def calcule(self):
        if self.D_projet["valid"]==[1,1,1]:
            if self.D_projet["methode"]==1:
                resultats=electre1.electre_i(np.array(self.D_projet["perf"]), self.D_projet["poids"], remove_cycles = False, c_hat = self.D_projet["seuilconc"], d_hat = self.D_projet["seuildisc"], graph = True)
            if self.D_projet["methode"]==2:
                resultats=electreis.electre_i_s(np.array(self.D_projet["perf"]), self.D_projet["seuilsq"], self.D_projet["seuilsp"], self.D_projet["seuilsveto"], self.D_projet["poids"], graph = True, lambda_value = self.D_projet["seuilconc"])
            if self.D_projet["methode"]==3:
                resultats=electreiv.electre_i_v(np.array(self.D_projet["perf"]), self.D_projet["seuilsveto"], self.D_projet["poids"], remove_cycles = False, c_hat = self.D_projet["seuilconc"], graph = True)
            if self.D_projet["methode"]==4:
                resultats=electre2.electre_ii(np.array(self.D_projet["perf"]), self.D_projet["poids"], c_minus = self.D_projet["seuilconc"], c_zero = self.D_projet["seuilconc2"], c_plus = self.D_projet["seuilconc3"], d_minus = self.D_projet["seuildisc"], d_plus = self.D_projet["seuildisc2"], graph = True)
            if self.D_projet["methode"]==5:
                resultats=electre3.electre_iii(np.array(self.D_projet["perf"]), self.D_projet["seuilsp"], self.D_projet["seuilsq"], self.D_projet["seuilsveto"], self.D_projet["poids"], graph = True)
            if self.D_projet["methode"]==6:
                resultats=electre4.electre_iv(np.array(self.D_projet["perf"]), self.D_projet["seuilsp"], self.D_projet["seuilsq"], self.D_projet["seuilsveto"], graph = True)
            if self.D_projet["methode"]==7:
                resultats=electretri.electre_tri_b(self.D_projet["choix"], np.array(self.D_projet["perf"]), self.D_projet["poids"], self.D_projet["seuilsq"], self.D_projet["seuilsp"], self.D_projet["seuilsveto"], self.D_projet["profils"], self.D_projet["seuilconc"], verbose = True, rule = self.D_projet["regle"], graph = True)
            self.resultats=resultats
            # resultats[-1].savefig(sys.path[0]+"/images/graph.jpg", bbox_inches='tight', dpi=150)
            resultats[-1].savefig(image_dir+"\graph.jpg", bbox_inches='tight', dpi=150)
            resultats[-1].clf()
            msg(self,"Le calcule est terminé vous pouvez affichez les résultats")
            

# implémentation de la fenêtre principale
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electre (Méthode multicitères)")
        self.setMinimumSize(820,600)
        palette=QPalette(QColor("lightblue"))
        self.setPalette(palette)
        
        # affectation du caractère multidocuments à l'interface
        self.mdi=QMdiArea(self)
        self.setCentralWidget(self.mdi)
        # definition du chemin des ressources
        self.path=sys.path
        # definition du processus de fermeture d'une fenêtre
        self.closeEvent=self.close_window
        # image et couleur de l'arrière plan
        # oImage = QImage(self.path[0]+"/images/chemins2.jpg")
        oImage = QImage(image_dir + "\chemins2.jpg")
        self.setAutoFillBackground(True)
        palette = self.palette() 
        palette.setColor(QPalette.Window, QColor(200,150,190))            #QPalette.Window= 10 = Windowrole
        self.setPalette(palette)
        self.mdi.setBackground(QBrush(oImage))
        # defintion de la barre d'outils
        toolbar=QToolBar("Barre d'outils principale")
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(16,16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # definition des actions
        # action d'ouverture de fichiers
        open=QAction(QIcon(image_dir+"\open.png"),"Ouvrir",self)
        open.setStatusTip("Ouvre un fichier déjà existant")
        open.triggered.connect(self.openAction)
        open.setShortcut(QKeySequence("Ctrl+o"))
        toolbar.addAction(open)
        # action de creation de nouveaux fichiers
        new=QAction(QIcon(image_dir+"\\new.png"),"Nouveau",self)
        self.nbtables=0
        new.setStatusTip("Ouvre un nouveau fichier")
        new.triggered.connect(self.newAction)
        new.setShortcut(QKeySequence("Ctrl+n"))
        toolbar.addAction(new)
        # action de sauvegarde de fichiers
        save=QAction(QIcon(image_dir+"\save.png"),"Enregistrer",self)
        save.setStatusTip("Sauvegarde le fichier en cours d'utilisation")
        save.triggered.connect(self.saveAction)
        save.setShortcut(QKeySequence("Ctrl+s"))
        toolbar.addAction(save)
        # action de fermeture de l'application
        quit=QAction(QIcon(image_dir+"\quit.png"),"Quitter",self)
        quit.setStatusTip("Ferme les fichiers et quitte l'application")
        quit.triggered.connect(self.quitAction)
        quit.setShortcut(QKeySequence("Ctrl+q"))
        toolbar.addAction(quit)
        # action d'affichage des fenêtres cachées
        affiche=QAction("afficher tout",self)
        affiche.triggered.connect(self.afficherAction)
        # action de masquage de toute les fenêtres
        masquer=QAction("masquer",self)
        masquer.triggered.connect(self.masquerAction)
        # action d'affichage de sortie
        sortie=QAction("sortie",self)
        sortie.triggered.connect(self.sortieAction)
        # definition de la barre d'état
        self.setStatusBar(QStatusBar(self))
        # definition des menus
        self.menu=self.menuBar()
        Fichier_menu=self.menu.addMenu("&Fichier")
        Fichier_menu.addAction(open)
        Fichier_menu.addAction(new)
        Fichier_menu.addAction(save)
        Fichier_menu.addAction(quit)
        Affichage_menu=self.menu.addMenu("&Affichage")
        Affichage_menu.addAction(affiche)
        Affichage_menu.addAction(masquer)
        self.Fenetre_menu=self.menu.addMenu("Fenêtres")
        
    # definition des slots d'actions
    # action neauveau projet
    def newAction(self):
        self.mdi.setVisible(True)
        self.nbtables += 1
        sub=n_table()
        sub.setWindowTitle("Projet n°"+str(self.nbtables))
        self.mdi.addSubWindow(sub)
        sub.setObjectName("prj"+str(self.nbtables))
        masquer=QAction("masquer",self)
        masquer.triggered.connect(sub.masquer_Action)
        afficher=QAction("afficher",self)
        afficher.triggered.connect(sub.afficher_Action)
        prj_menu=self.Fenetre_menu.addMenu("Projet n°"+str(self.nbtables))
        prj_menu.addAction(masquer)
        prj_menu.addAction(afficher)
        
        sub.move(150+self.nbtables*20,50+self.nbtables*20)
        sub.edit_titre.setText("Projet n°"+str(self.nbtables))
        sub.edit_titre.selectAll()
        sub.edit_titre.setFocus()
        sub.show()
        return(sub)
    # action ouvrir un projet
    def openAction(self):
        sub=self.newAction()
        sub.hide()
        try:
            ok=sub.open_project()
            if not(ok):
                for action in self.Fenetre_menu.actions():
                    if action.text()==sub.windowTitle():
                        self.Fenetre_menu.removeAction(action)
        except:
            for action in self.Fenetre_menu.actions():
                if action.text()==sub.windowTitle():
                    print(action.text())
                    self.Fenetre_menu.removeAction(action)
            sub.deleteLater()
            return
        sub.setFocus(True)
        # sub.setWindowTitle(sub.D_projet["titre"])
        #sub.Projet.setEnabled(True)
        #sub.reitialise_proj.setEnabled(True)
        #sub.valider_poids.setEnabled(True)
        sub.valide_proj()
        sub.Projrt_Parametres.setCurrentIndex(0)

    # action sauvegarder un projet
    def saveAction(self):
        for win in self.mdi.subWindowList():
            if  win.objectName()[0:3]=="prj":
                win.save_project()
    # action quitter l'application
    def quitAction(self,s):
        app.closeAllWindows()
    # action afficher les fenêtres masquées
    def afficherAction(self):
        for win in self.mdi.subWindowList():
            win.show()
        self.mdi.cascadeSubWindows()
    # action masquer les fenêtres visibles
    def masquerAction(self):
        for win in self.mdi.subWindowList():
            win.hide()
    # action générer un fichier de sortie
    def sortieAction(self,sender):
        D=sender.D_projet
        R=sender.resultats
        C=sender.choix_dic
        N=str(sender.objectName()[3:])
        sub=doc_sortie()
        self.mdi.addSubWindow(sub)
        sub.move(20,10)
        sub.setObjectName("sortie"+sender.objectName())
        sub.setWindowTitle("Resultat n°"+N)
        
        masquer=QAction("masquer",self)
        masquer.triggered.connect(sub.masquer_Action)
        afficher=QAction("afficher",self)
        afficher.triggered.connect(sub.afficher_Action)
        prj_menu=self.Fenetre_menu.addMenu("Resultat n°"+N)
        prj_menu.addAction(masquer)
        prj_menu.addAction(afficher)
        
        sub.sortie.setAcceptRichText(True)
        sub.sortie.setFontPointSize(18)
        sub.sortie.setTextColor(QColor("green"))
        sub.sortie.setFontUnderline(True)
        sub.sortie.setPlainText("Les données du projet: "+str(D["titre"])+"\n")
        sub.sortie.setFontUnderline(False)
        sub.sortie.setTextColor(QColor("darkblue"))
        sub.sortie.setFontPointSize(16)
        html_text="<body><br>"+"Méthode: "+D["n_methode"]+"<br>"+"Nombre d'alternatives: "+str(D["nbchoix"])+"<br>"+"Nombre de critères: "+str(D["nbcriteres"])+"<br>"
        html_text+="<br>Paramètres de la méthode:"
        data,i,cols,allrows,rows=[],0,D["criteres"],["poids","seuils p","seuils q","seuils du veto"],[]
        for row in list([D["poids"],D["seuilsp"],D["seuilsq"],D["seuilsveto"]]):
            if row!=[]:
                data.append(row)
                rows.append(allrows[i])
            i+=1
        html_text+=self.html_table(rows,cols,data)
        html_text+="<br>Performances des alternatives:"
        html_text+=self.html_table(D["choix"],D["criteres"],D["perf"])
        sub.sortie.append(html_text)
        sub.show()
# -------sorties de chaque verssion electre--------------
# eI: concordance, discordance, dominance, kernel, dominated
# eIv: concordance, discordance, dominance, kernel, dominated
        if D["methode"]==1 or D["methode"]==3:
            html_text= "<br>Table de concordance:"
            html_text+=self.html_table(D["choix"],D["choix"],np.round(R[0],2))
            html_text+= "<br><br>Table de discordance:"
            html_text+=self.html_table(D["choix"],D["choix"],np.round(R[1],2))
            html_text+= "<br><br>Table de surclassement:"
            html_text+=self.html_table(D["choix"],D["choix"],R[2])
            html_text+= "<br><br>Les éléments du noyau:<br>"
            html_text+= self.html_liste(R[3],C)
            html_text+= "<br><br>Les alternatives surclassées:<br>"
            html_text+= self.html_liste(R[4],C)
            sub.sortie.append(html_text)
            sub.show()
# eIs: global_concordance, discordance, kernel, credibility, dominated
        if D["methode"]==2:
            html_text= "<br>Table de concordance globale:"
            html_text+=self.html_table(D["choix"],D["choix"],np.round(R[0],2))
            html_text+= "<br><br>Table de discordance:"
            html_text+=self.html_table(D["choix"],D["choix"],R[1])
            html_text+= "<br><br>Les éléments du noyau:<br>"
            html_text+= self.html_liste(R[2],C)
            html_text+= "<br><br>Table de crédibilité:"
            html_text+=self.html_table(D["choix"],D["choix"],R[3])
            html_text+= "<br><br>Les alternatives surclassées:<br>"
            html_text+= self.html_liste(R[4],C)
            sub.sortie.append(html_text)
            sub.show()
# eII: concordance, discordance, dominance_s, dominance_w, rank_D, rank_A, rank_M, rank_P
        if D["methode"]==4:
            html_text= "<br>Table de concordance:"
            html_text+=self.html_table(D["choix"],D["choix"],np.round(R[0],2))
            html_text+= "<br>Table de discordance:"
            html_text+=self.html_table(D["choix"],D["choix"],np.round(R[1],2))
            html_text+= "<br>Table de surclassement S:"
            html_text+=self.html_table(D["choix"],D["choix"],R[2])
            html_text+= "<br>Table de surclaement W:"
            html_text+=self.html_table(D["choix"],D["choix"],R[3])
            html_text+= "<br>L'ordre D:<br>"
            html_text+=self.html_rank(R[4],C)
            html_text+= "<br>L'ordre A:<br>"
            html_text+=self.html_rank(R[5],C)
            html_text+= "<br>L'ordre M:<br>"
            html_text+=self.html_liste(R[6],C)
            html_text+= "<br>Table de l'ordre P:"
            html_text+=self.html_table(D["choix"],D["choix"],R[7])
            sub.sortie.append(html_text)
            sub.show()
# eIII: global_concordance, credibility, rank_D, rank_A, rank_M, rank_P
# eIV: credibility, rank_D, rank_A, rank_M, rank_P
        if D["methode"]==5 or D["methode"]==6:
            if D["methode"]==5:
                html_text= "<br>Table de concordance globale:"
                html_text+=self.html_table(D["choix"],D["choix"],np.round(R[0],2))
            if D["methode"]==5: i=6
            else:i=5
            html_text+= "<br><br>Table de crédibilité:"
            html_text+=self.html_table(D["choix"],D["choix"],R[i-5])
            html_text+= "<br>L'ordre D:<br>"
            html_text+=self.html_liste(R[i-4],C)
            html_text+= "<br>L'ordre A:<br>"
            html_text+=self.html_liste(R[i-3],C)
            html_text+= "<br>L'ordre M:<br>"
            html_text+=self.html_liste(R[i-2],C)
            html_text+= "<br>Table de l'ordre P:"
            html_text+=self.html_table(D["choix"],D["choix"],R[i-1])
            sub.sortie.append(html_text)
            sub.show()
# eTri: classification
        if D["methode"]==7: 
            html_text= "<br>Table des profiles:"
            profils=[D["choix"][int(i)] for i in [D["profils"][j][-1] for j in range(len(D["profils"]))]]
            print(D["profils"])
            html_text+=self.html_table(profils,D["criteres"],D["profils"])
            html_text+= "<br>Classification:<br>"
            categorie=""
            categories=list(set(R[0]))
            html_text+="<br> Nombre de catégories: "+str(len(categories))+"<br><br>"
            indx=0
            for i in categories:
                indx+=1
                categorie+=("Catégorie "+str(indx)+": ")
                ji=0
                fl=0
                for j in R[0]:
                    if j==i: 
                        if fl != 0:
                            categorie+=", "
                        categorie+=(D["choix"][ji])
                        fl=1  
                    ji+=1
                fl=0
                html_text+=categorie+"<br><br>"
                categorie=""
            
            
            
            sub.sortie.append(html_text)
            sub.show()
            
        graph_img=image_dir+"\graph.jpg"
        html_text='<br> Representation graphique du résultat:<br><br><br><img src='+graph_img+' alt="graphe" width="700" height="500">'
        sub.sortie.append(html_text)
        # --------------
        
        # -------------
        sub.show()
    # fonctions convertissant les données de sorties en element html
    # préparation d'une table en html
    def html_table(self,rows,cols,data):
        html_text="<style>table,th,td{border:2px solid darkblue;border-collapse:collapse;text-align:center}</style><table><tr><th>--------</th>"
        for i in range(len(cols)):
            html_text+="<th> "+cols[i]+" </th>"
        html_text+="</tr>"
        for i in range(len(rows)):
            html_text+="<tr>"
            html_text+="<th> "+rows[i]+" </th>"
            for j in range(len(cols)):
                html_text+="<td> "+str(data[i][j])+" </td>"
            html_text+="</tr>"
        html_text+="</table></body><br>"
        return html_text
    # préparation d'une liste en html
    def html_liste(self,lalist,C):
        html_text="<b>"
        for i in range(len(lalist)):
            if i!=0: html_text +=", "
            if len(lalist[i])==2:
                html_text +=C[lalist[i]]
            else:
                html_text +="("
                for j in range(0,len(lalist[i]),4):
                    if j!=0: html_text +=", "
                    html_text +=C[lalist[i][j:j+2]]
                html_text +=")"
        html_text +=".</b><br>"
        return html_text
    # préparation d'un ordre en html
    def html_rank(self,rank,C):
        html_text="<b>"
        for i in range(len(rank)):
            if len(rank[i])==1:
                if i!=0: html_text +=", "
                html_text +=C[rank[i][0]]
            else:
                if i!=0: html_text +=", "
                html_text += "("
                for j in range(len(rank[i])):
                    if j!=0: html_text +=", "
                    html_text +=C[rank[i][j]]
                html_text += ")"
        html_text +=".</b><br>"
        return html_text
    # fermer une fenêtre
    def close_window(self,event):
        if QMessageBox.warning(self, 'Attention!', "La sauvegarde n'est pas automatique. \nN'appuyez sur Ok que si vous avez préalablement sauvegardé vos projets!", QMessageBox.Ok, QMessageBox.Cancel)==QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
        
# la boucle principale
app=QApplication(sys.argv)
window=MainWindow()
window.showMaximized()
sys.exit(app.exec_())