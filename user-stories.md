## User stories et leurs critères d'acceptation

**US00 : Mise en place du setup technique**
En tant que développeur, je veux mettre en place les bases de données et la structure du projet afin de pouvoir développer les fonctionnalités. 

*Critères d'acceptation* : 
- La base SQLite est créée pour stocker les identifiants et mots de passe (hachés) des utilisateurs.
- La base MongoDB est créée et connectée, prête à accueillir une collection "questions".
- Les connexions aux bases sont testées et fonctionnelles.
&nbsp;

**US01 : Inscription**
En tant qu’enseignant, je veux créer un compte avec un identifiant et un mot de passe afin d’accéder à l’application.

*Critères d'acceptation* : 
- L’utilisateur peut saisir un identifiant et un mot de passe.
- Le mot de passe est stocké de manière sécurisée (hachage).
- Un message s’affiche pour confirmer la création du compte.
&nbsp;

**US02 : Connexion**
En tant qu’enseignant, je veux me connecter avec mon identifiant et mon mot de passe afin d’accéder à mes fonctionnalités.

*Critères d'acceptation* :
- Si identifiant/mot de passe correct = message de confirmation.
- Si identifiant/mot de passe incorrect = un message d’erreur.
&nbsp;

**US03 : Consulter les questions**
En tant qu’enseignant, je veux voir la liste des questions disponibles afin de vérifier celles déjà créées.

*Critères d'acceptation* :
- L’IHM affiche la liste de toutes les questions présentes en base.
- Chaque question affiche son énoncé, ses réponses possibles ainsi que son thème et le type de test.
&nbsp;

**US04 : Ajouter des questions**
En tant qu’enseignant, je veux ajouter une nouvelle question avec ses réponses possibles afin d’alimenter ma base de questions.

*Critères d'acceptation* :
- Le formulaire permet de saisir : énoncé, thème, type de test, réponses possibles, la ou les réponse(s) correcte(s).
- Le formulaire est enregistrée dans MongoDB.
- Un message de confirmation apparaît après ajout.
&nbsp;

**US05 : Supprimer des questions**
En tant qu’enseignant, je veux supprimer une question afin de maintenir ma base de questions à jour.

*Critères d'acceptation* :
- Chaque question de la liste propose un bouton "Supprimer".
- La question est retirée de MongoDB après confirmation.
- L’IHM met à jour la liste sans la question supprimée.
&nbsp;

**US06 : Générer un quiz**
En tant qu’enseignant, je veux générer un quiz aléatoire avec un nombre de questions choisi afin de préparer une évaluation rapidement.

*Critères d'acceptation* :
- L’utilisateur a le choix entre 5 ou 10 questions.
- L’API sélectionne aléatoirement des questions dans MongoDB.
- Le quiz est affiché sur l’IHM une fois généré.
- Une simulation du quiz est possible pour tester.
&nbsp;

**US07 : Sauvegarder un quiz généré**
En tant qu’enseignant, je veux sauvegarder un quiz généré  avec les questions aléatoirement choisies pour le conserver et le réutiliser plus tard.

*Critères d'acceptation* :
- Un bouton “Sauvegarder le quiz” doit être disponible.
- L’enseignant peut attribuer un nom ou un titre au quiz au moment de la sauvegarde.
- L’enseignant peut recharger un quiz sauvegardé pour l’utiliser à nouveau.
- Les quiz sont bien sauvegardés en base et restent disponibles même après déconnexion ou fermeture de l’application.
&nbsp;

**US08 : Quiz par thème ou type de test**
En tant qu’enseignant, je veux générer un quiz en choisissant un thème ou un type de test afin d’adapter mon évaluation.

*Critères d'acceptation* :
- L’IHM propose une liste déroulante avec les thèmes et les tests disponibles.
- L’API sélectionne aléatoirement des questions uniquement dans le thème et/ou le type de test choisi.
- Si aucun thème/test n’est sélectionné, la génération de quiz se fait de manière aléatoire sur toutes les questions (comportement par défaut).
&nbsp;

**US09 : Déconnexion**
En tant qu’enseignant, je veux pouvoir me déconnecter afin de quitter l’interface.

*Critères d'acceptation* :
- L’IHM affiche un bouton "Déconnexion".
- En cliquant dessus, l’utilisateur est redirigé automatiquement vers la page de connexion.

