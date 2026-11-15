# MédiParc NFC

Démo d'application iPhone pour gérer un parc de matériel médical en location, avec identification par puces NFC.

## Contenu

- `index.html` + `photos/` : l'interface (une page web sans dépendance), pensée pour l'iPhone 15 Pro Max, thème clair et sombre.
- `ios/` : le projet Xcode. L'app affiche l'application en ligne (ou la démonstration embarquée hors connexion) et branche la lecture NFC de l'iPhone (Core NFC).
- `server/` : le serveur (comptes, base partagée, ordonnances, facturation).

Écrans : tableau de bord, inventaire du parc (liste ou plan de Tahiti), scan NFC, locations par bénéficiaire, entretien (désinfection, maintenance, contrôles). Tarifs en francs pacifiques (XPF). Toutes les données sont fictives et reviennent à zéro à chaque lancement (seules les puces associées sont mémorisées).

## Ouvrir dans Xcode

1. Ouvrir `ios/MediParcNFC.xcodeproj` (Xcode 16 ou plus récent).
2. Cible MediParcNFC > Signing & Capabilities : choisir votre équipe et, si besoin, changer l'identifiant `com.mediparc.nfc`.
3. Brancher l'iPhone, le choisir comme destination, puis lancer (⌘R).

La lecture NFC demande un compte Apple Developer payant (la capacité « NFC Tag Reading » n'est pas proposée aux comptes gratuits) et un vrai iPhone. Avec un compte gratuit, retirez la capacité NFC dans Signing & Capabilities : l'app se lance quand même et simule le scan, comme dans le simulateur.

## Tableau de bord et rapports

L'accueil reprend la maquette « ManaProcess » : barre d'application (recherche, alertes, menu), taux d'occupation, quatre tuiles, liste « À traiter », courbe d'occupation et répartition du parc. La barre d'onglets donne accès à Accueil, Parc, Locations, Entretien, Rapports et Plus ; le bouton central ouvre les actions rapides (dont le scan NFC). L'écran Entretien présente deux tuiles (contrôles à venir, actions en cours), le matériel à désinfecter, en maintenance, et les prochains contrôles sur 7 ou 30 jours. L'écran Locations sépare les contrats en cours, à renouveler (retour sous 14 jours) et terminés (historique de démonstration), avec tri, filtre par commune et menu par bénéficiaire. L'écran Parc propose quatre vues (Liste, Plan, Statistiques, Maintenance), des tuiles par état, des favoris et un menu d'actions par carte. L'historique d'occupation et la tendance « +5 % » sont des valeurs de démonstration.

## Rapports

Cinq vues : Vue d'ensemble (rentabilité du parc, tuiles, courbe d'occupation sur 7 jours, 30 jours ou 12 mois, répartition, activité), Rentabilité (classement par équipement), Utilisation (jours de location cumulés), Activité, Exports (inventaire, contrats, rentabilité copiés au format CSV). Les tendances « +5 % » et « +12 % » et les courbes passées sont des valeurs de démonstration.

## Rentabilité

Chaque fiche compare les loyers encaissés depuis l'achat au prix d'achat (pourcentage amorti, semaines restantes ou bénéfice). L'onglet Rapports donne la synthèse du parc et le classement par équipement. Les prix d'achat viennent du catalogue quand il en donne un plausible, sinon ils sont estimés (indiqué « estimé ») ; les jours de location passés sont des valeurs de démonstration.

## Catalogue

Le parc reprend les 24 produits du catalogue de location (lits, porte-sérum, lève-personnes, déambulateurs et rollators, fauteuil roulant, TENS, aérosols, concentrateur d'O2, aspirateur, tire-lait). Le « prix catalogue » de chaque fiche vient de cette liste ; les loyers hebdomadaires, les bénéficiaires et les dates sont des valeurs de démonstration. Les photos sont des illustrations libres par type de matériel, pas les modèles exacts ; trois produits n'ont pas encore de photo et affichent une icône.

## Pharmacies

Chaque location est rattachée à la pharmacie qui l'a délivrée. Elle apparaît dans la fiche de l'équipement, sous chaque ligne de l'écran Locations, dans les contrats terminés, dans l'export des contrats et dans Rapports (« Locations par pharmacie »). L'entonnoir de l'écran Locations filtre par pharmacie ; elle se choisit à la mise en location. Les trois pharmacies de la démo sont fictives.

## Durée des locations

Chaque fiche en location affiche depuis combien de temps le matériel est loué, combien de temps il reste, la durée prévue et une barre de progression ; « + 1 semaine » repousse le retour. La durée prévue se choisit à la mise en location (1, 2, 4 semaines ou 3 mois). L'écran Locations et les cartes du Parc reprennent ces durées.

## Puces NFC : un lien par équipement

Chaque puce contient un lien (enregistrement NDEF de type URI), par exemple `https://manaprocess.cloud/materiel/LIT-0101`. À la lecture, l'app retrouve l'équipement dont le lien est identique, ou dont la référence termine le lien.

Bouton « Paramètres » en haut à droite :

- Écrire le lien sur une puce : l'app programme une puce vierge ou réinscriptible avec le lien de l'équipement.
- Lire une puce déjà programmée : le lien présent sur la puce est associé à l'équipement.
- Saisir le lien à la main, le copier, ou retirer la puce.
- Adresse des liens : le début commun des liens (par défaut `https://manaprocess.cloud/materiel/`, modifiable).
- Tester une puce, effacer toutes les puces, rétablir les liens par défaut.

Les associations sont mémorisées sur l'appareil. Une puce lue hors de l'app ouvre son lien dans Safari : il faut donc qu'une page existe à cette adresse sur manaprocess.cloud.

## Plan

Le plan dessiné montre où se trouve le matériel (dépôt ou domicile du bénéficiaire, adresses fictives). Dans l'app iPhone, « Zoomer » ouvre la vraie carte Apple Plans, zoomable jusqu'à l'adresse, avec l'itinéraire. Dans la démo en ligne, « Zoomer » ouvre Apple Plans dans le navigateur.

## Application en ligne : comptes, base partagée, portail pharmacies

Adresse : `https://manaprocess.cloud/materiel/`. Tout le monde (iPhone, Android, ordinateur) travaille sur la même base de données.

- **Comptes** : rôles administrateur (tout, y compris les comptes), équipe du parc (parc, locations, entretien, puces, facturation) et pharmacie. L'administrateur crée les comptes dans Plus > Comptes et pharmacies ; chaque nouveau compte reçoit un mot de passe provisoire à changer à la première connexion.
- **Portail pharmacie** : une pharmacie ne voit que ses locations en cours et terminées, ses bénéficiaires, ses ordonnances et sa facturation. Le serveur filtre les données : l'historique d'un équipement ne montre jamais les autres pharmacies.
- **Ordonnances** : le serveur n'étant pas certifié HDS, aucun fichier d'ordonnance n'y est envoyé. La pharmacie conserve l'ordonnance et confirme dans la fiche de la location qu'elle l'a vérifiée (date, numéro interne facultatif) ; l'auteur et l'heure sont enregistrés, et la date figure dans l'export de facturation. Les locations non confirmées apparaissent dans « À traiter ». **Rappel de nouvelle ordonnance** : la pharmacie indique jusqu'à quand l'ordonnance est valable ; l'application signale « Nouvelle ordonnance à prévoir » quand elle expire dans les 14 jours ou finit avant la fin de location prévue (après une prolongation, par exemple), et « Ordonnance expirée » ensuite. Le rappel disparaît dès que la nouvelle ordonnance est enregistrée. « Scanner » prend la photo et « Importer un fichier » accepte n'importe quel format (les images lisibles par le navigateur sont converties en PDF, les autres formats et les PDF sont conservés tels quels) ; le fichier est préparé sur l'appareil et l'enregistre directement sur le serveur de la pharmacie : dans le dossier réseau choisi (Chrome ou Edge sur ordinateur, dossier mémorisé sur le poste), via « Enregistrer dans Fichiers » (iPhone, Android, app iPhone) ou par téléchargement. Le nom du fichier (`Ordonnance_date_référence_initiales`) devient le numéro interne de la vérification. « Voir l'ordonnance » relit le fichier sur le serveur local de la pharmacie (recherche par référence dans le dossier choisi sur ordinateur, ou sélection dans Fichiers sur téléphone) et l'affiche sur l'appareil, sans passer par Internet. Le dépôt de fichiers existe dans le code mais reste désactivé ; ne l'activer (`DOCUMENTS_ENABLED=1`) que sur un hébergement certifié HDS.
- **Géolocalisation au scan** : chaque lecture de puce (app iPhone, Chrome sur Android, ou lien ouvert depuis la puce) enregistre la date, la personne et la position du téléphone si elle est autorisée. La fiche affiche le dernier scan avec un lien vers la carte.
- **Android** : Chrome lit et écrit les puces NFC directement (Web NFC) et propose d'installer l'application sur l'écran d'accueil.
- **Facturation** : par mois et par pharmacie, jours de location dans le mois × tarif hebdomadaire ÷ 7 (le jour du retour n'est pas facturé). Export CSV pour Excel ou un logiciel de facturation. Le mois en cours est prévisionnel.

- **Photos horodatées du matériel** : depuis la fiche, « Prendre une photo horodatée » (livraison, retour, état, panne). Date, heure, référence, auteur et position sont incrustés sur l'image ; le serveur enregistre aussi sa propre heure et la position. Chaque photo apparaît aussi en vignette dans l'historique de l'équipement, à sa date. Les photos prises pendant une location sont visibles par la pharmacie concernée et supprimées 3 ans après la fin de cette location.

- **E-mails de rappel aux pharmacies** : chaque jour à l'heure choisie (7 h par défaut, heure de Tahiti), chaque pharmacie reçoit un e-mail s'il y a du nouveau : ordonnance à confirmer (2 jours après le début de la location), à renouveler (14 jours puis 3 jours avant l'expiration, ou plus courte que la location), expirée. Chaque rappel n'est envoyé qu'une fois par étape ; une nouvelle ordonnance relance le cycle. Le patient n'y figure que par ses initiales et sa commune, avec un lien vers la fiche (connexion obligatoire). Réglages : Plus > Comptes et pharmacies (adresses, activation, heure, test, aperçu) ; chaque pharmacie peut changer son adresse (Plus > E-mail des rappels). Service d'envoi : variables `MAIL_PROVIDER` (resend, brevo ou smtp), `MAIL_API_KEY` ou `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASS`, et `MAIL_FROM`.

### Données personnelles

- **Aucune information médicale** : ni ordonnance, ni pathologie, ni motif, ni prescripteur. Un bénéficiaire = nom, adresse, commune, téléphone.
- **Chiffrement** : nom, adresse et téléphone sont chiffrés en AES-256-GCM dans la base et dans ses sauvegardes. La clé (`DATA_KEY`) est stockée dans les variables du projet sur le VPS, séparément des données : la conserver aussi en lieu sûr, car sans elle les noms ne peuvent plus être lus.
- **Conservation** : 3 ans après la fin de sa dernière location, un bénéficiaire est anonymisé automatiquement (nom remplacé, adresse, téléphone et position effacés). Les positions de scan et numéros d'ordonnance de plus de 3 ans sont effacés. Les montants et dates restent pour la comptabilité.
- **À prévoir** : désigner un référent pour la protection des données et tenir le registre des traitements.

### Serveur

`server/server.js` : Node 22 sans dépendance externe (SQLite, http et crypto intégrés). Mots de passe chiffrés (scrypt), sessions par cookie sécurisé, limitation des tentatives de connexion, sauvegarde quotidienne de la base (14 jours conservés).

Essai en local :

```bash
deploy/build.sh && COOKIE_SECURE=0 ADMIN_PASSWORD=MotDePasse2026 node server/server.js
```

Puis ouvrir `http://localhost:3000/materiel/` (identifiant `admin`).

### Sur le VPS

Le projet Docker `mediparc-nfc` (`deploy/docker-compose.yml`) télécharge ce dépôt (qui doit rester public) à chaque démarrage, génère le site et lance le serveur derrière Traefik. Les données sont dans le volume `mediparc-data`. Pour publier une nouvelle version : pousser sur la branche, puis redémarrer le projet. Au premier démarrage, la base est remplie avec les données de démonstration.

## Demandes des pharmacies et suivi du grossiste

- **Portail pharmacie** : depuis l'accueil, le bouton + ou la fiche d'un matériel, la pharmacie envoie une demande de
  **location** (matériel du catalogue, bénéficiaire, durée, date souhaitée), de **reprise**, de **prolongation** ou
  signale un **problème**. Elle suit l'état de ses demandes (nouvelle, planifiée, effectuée, refusée) dans
  Locations › Demandes, et peut créer un bénéficiaire. Catalogue avec tarifs et disponibilité.
- **Portail grossiste** : nouvelles demandes sur l'accueil et dans la cloche ; chaque demande se planifie (date de
  passage), se traite (livraison d'un équipement disponible, reprise, prolongation, réparation) ou se refuse avec un
  motif. Locations › **Planning** regroupe sur 14 jours les livraisons, reprises et fins de location par jour et par
  commune (bouton Copier pour l'envoyer au livreur). **Suivi des pharmacies** : locations, loyers, retards,
  ordonnances à traiter et demandes, pharmacie par pharmacie.
- E-mails (si l'envoi est configuré) : la pharmacie est prévenue quand sa demande est planifiée, traitée ou refusée
  (patient désigné par ses initiales) ; l'équipe reçoit les nouvelles demandes à l'adresse réglée dans
  Comptes et pharmacies › E-mails.
- Les précisions saisies sont chiffrées, limitées à 300 caractères, effacées après 3 ans, et ne doivent contenir
  aucune information médicale.

## Guides d'utilisation et liseuse intégrée

Chaque guide se lit **dans le portail**, dans une liseuse (sommaire cliquable, vignettes des pages, zoom,
page suivante/précédente au clavier) avec un bouton **Télécharger le PDF**.

- `guides/guide-pharmacie.pdf` : portail pharmacie, sur ordinateur (demandes, suivi, locations, ordonnances,
  e-mails, facturation). Accessible sans connexion depuis l'écran de connexion, et depuis l'accueil et le menu Plus.
- `guides/guide-administrateur.pdf` : **guide du grossiste**, sur ordinateur (demandes des pharmacies, planning,
  suivi des pharmacies, parc, entretien, rapports, facturation, comptes, données). Réservé à l'équipe.
- `guides/guide-technicien.pdf` : technicien et livreur, sur téléphone (tournée, scan NFC, livraison, reprise,
  désinfection, panne, contrôles, pose des étiquettes, aide-mémoire). Réservé à l'équipe.
- `guides/pages/<guide>/` : pages en images et sommaire (`index.json`) servis à la liseuse
  (`/materiel/api/guides/<guide>/index.json` et `NN.jpg`, mêmes droits que le PDF).
- Régénération : serveur de démonstration neuf
  (`DATA_DIR=<dossier vide> ADMIN_PASSWORD=Provisoire2026 COOKIE_SECURE=0 PORT=3456 node server/server.js`),
  puis `node guides/outils/capture.js <captures> <photo-lit.jpg> <photo-ordonnance.jpg>` et
  `python3 guides/outils/build.py <captures> guides`. Le texte est dans `guides/outils/contenu.py`.

## Version ordinateur

Au-delà de 1 024 px de large, le portail passe en mise en page bureau : menu latéral, contenu large,
fiche d'un matériel en panneau à droite, fenêtres centrées. Sur téléphone, la mise en page mobile est inchangée.

## Icône

`icons/` contient l'icône (1024 px et tailles web) et sa source `icon-source.html`. Elle sert d'icône à l'app iPhone (Assets.xcassets) et à l'ajout sur l'écran d'accueil depuis Safari (nom « MédiParc »).

## Modifier l'interface

Modifier `index.html` à la racine, puis recopier dans le projet Xcode :

```bash
ios/sync-web.sh
```

Photos du matériel : Wikimedia Commons (auteurs et licences dans l'écran Parc, « Crédits photos »).
