#! /usr/bin/python3
import os
import sys
import signal
liste = {}#J'utilise un dictionnaire pour stocker les processus et les pid(clé)

#Mon main, dans lequel je crée le signal et démarre mon shell
def main():
    os.system("reset")#pour pouvoir reset lorsque le shell commence
    signal.signal(signal.SIGCHLD, filsKill)
    while True:#Boucle pour mon shell
        shell()

#Mon shell, dans lequel je fait le input avec la commande, et toute mes options
#sont la; quitter, liste, tuer, si l'utilisateur n'entre pas une de ces commandes
#il y a juste execution de la commande.
def shell():
    commande = input("{0}$?>".format(os.getenv("USER")))#Input, avec le nom d'utilisateur
    commande = commande.strip()
    argv = commande.split(" ")#Je sépare ma commande en deux, a partir de l'espace

    if argv[0] == 'quitter':#Si la commande est quitter, on va a la methode quitter
        quitter()

    elif argv[0] == 'liste':#Si la commande est liste, on affiche la liste des programmes
        list()

    elif argv[0] == 'tuer':#Si la commande est tuer, on tue le processus avec le pid(argv[1])
        kill(argv)

    elif len(argv[0]) > 0:#Sinon on execute juste la commande
        executer(argv)

#Commande quitter, j'affiche la liste des processus actifs avec une boucle,
#et je demande si il veut les tuer. Avec une boucle, je tue chacun des processus.
def quitter():
    if len(liste) > 0:#Si la liste contient aumoins 1 processus en cours
        print("Il reste des processus actifs:")
        for key in liste:#POur chaque clé dans mon dictionnaire liste
             print(key, liste[key][0])#Afficher pid et le nom du programme

        choix = input ("Voulez-vous les tuer (o/n)?")
        if choix == 'o':
            for key in liste:#On utilise os.kill et le signal SIGKILL
                os.kill(key, signal.SIGKILL)#Je tue la clé qui correspond au pid
            sys.exit(1)#Quitte le shell, le programme
        else:
            shell()

    sys.exit(1)

#Commande liste, pour afficher avec une boucle for, la liste des processus actifs
def list():

    for key in liste:#Pour chaque clé dans mon dictionnaire liste
        print(key, liste[key][0])#Afficher le pid et le nom du programme en cours

    shell()#Une fois la commande terminé, je retourne au shell

#Commande tuer, pour tuer un programme en cours avec son pid
def kill(argv):#argv qui correspond a la commande rentré divisé a partir de l'espace
    pidCle = argv[1]#le pid, correspond a argv[1] dans la commande
    pidCle = int(pidCle)#Important de caster en int, car on manipule des entiers

    if pidCle in liste.keys():#Si le pid se trouve dans les clés du dictionnaire
        os.kill(pidCle, signal.SIGKILL)#Tuer le programme avec son pid, os.kill et SIGKILL
    else:#Si le processus n'est pas dans le dictionnaire, afficher le message
        print("Processus n'est pas dans la liste de processus")

    shell()#Retourner dans le shell, apres avoir fait le traitement ou afficher
    #le message

#Executer la commande rentré par l'utilisateur
def executer(argv):#argv qui correspond a la commande rentré divisé a partir de l'espace
    tube = os.pipe()#Creer le tube pour pouvoir rediriger les erreurs
    pid = os.fork()#Créer un fork, processus fils a partir du pere


    if pid == 0:#FILS
        os.close(tube[0])#Fermer le tube[0], pere
        #Utilisation de dup2, pour pouvoir rediriger les erreurs dans le tube
        os.dup2(tube[1],2)

        #Afficher le programme déclenché
        print("\nProgramme {0} declenche avec le pid {1}".format(argv[0], os.getpid()))
        #Réafficher le nom pour le terminal, pour ne pas retourner a une ligne vide
        print(("{0}$?>".format(os.getenv("USER"))), end="", flush=True)
        os.execvp(argv[0], argv)#Executer la commande, le programme

    elif pid > 0:#PERE
        #Ajouter le programme, le pid et le tube dans le dictionnaire
        liste[pid] = [argv[0], tube]


#Méthode filskill qui se déclence lorsque le fils est tué, mort
def filsKill(signalnum, status):#NUmero du signal et le status en parametre
    pid, status = os.wait()#On fait le os.wait du pere

    #Si le statut ne retourne pas 0, ca veut dire qu'il y a des erreurs lié
    #a la commande, il faut donc rediriger ses erreurs dans le fichier.txt
    if status != 0:
        os.close(liste[pid][1][1])#Fermer le tube (dans mon dictionnaire liste)
        lecture = os.fdopen(liste[pid][1][0])
        erreur = lecture.read()

        #Append "a", on ajoute dans le fichier
        with open("erreur.txt", "a") as fichierErreur:
            print("\n##############################################################################"
            , file = fichierErreur, flush= True)
            print(liste[pid][0], file = fichierErreur, flush= True)
            print("\n{0}".format(erreur), file = fichierErreur, flush= True)

        #fichierErreur.close()#Fermer le fichier

    global liste
    liste.pop(pid)#Retirer le programme et son pid du dictionnaire liste
    print("\nLe processus {} est termine".format(pid))#Message pour dire terminé
    print(("{0}$?>".format(os.getenv("USER"))), end="", flush=True)

#Le vrai main du programme, j'appelle juste la fonction main()
#qui s'occupe de démarrer le shell() et de créer le signal
main()
