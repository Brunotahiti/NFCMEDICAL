# MédiParc NFC

Démo d'application iPhone pour gérer un parc de matériel médical en location, avec identification par puces NFC.

## Contenu

- `index.html` + `photos/` : l'interface (une page web sans dépendance), pensée pour l'iPhone 15 Pro Max, thème clair et sombre.
- `ios/` : le projet Xcode. L'app affiche cette interface et branche le bouton de scan sur la vraie lecture NFC de l'iPhone (Core NFC).

Écrans : tableau de bord, inventaire du parc (liste ou plan de Tahiti), scan NFC, locations par bénéficiaire, entretien (désinfection, maintenance, contrôles). Tarifs en francs pacifiques (XPF). Toutes les données sont fictives et reviennent à zéro à chaque lancement (seules les puces associées sont mémorisées).

## Ouvrir dans Xcode

1. Ouvrir `ios/MediParcNFC.xcodeproj` (Xcode 16 ou plus récent).
2. Cible MediParcNFC > Signing & Capabilities : choisir votre équipe et, si besoin, changer l'identifiant `com.mediparc.nfc`.
3. Brancher l'iPhone, le choisir comme destination, puis lancer (⌘R).

La lecture NFC demande un compte Apple Developer payant (la capacité « NFC Tag Reading » n'est pas proposée aux comptes gratuits) et un vrai iPhone. Avec un compte gratuit, retirez la capacité NFC dans Signing & Capabilities : l'app se lance quand même et simule le scan, comme dans le simulateur.

## Durée des locations

Chaque fiche en location affiche depuis combien de temps le matériel est loué, combien de temps il reste, la durée prévue et une barre de progression ; « + 1 semaine » repousse le retour. La durée prévue se choisit à la mise en location (1, 2, 4 semaines ou 3 mois). L'écran Locations et les cartes du Parc reprennent ces durées.

## Puces NFC : un lien par équipement

Chaque puce contient un lien (enregistrement NDEF de type URI), par exemple `https://votre-site.pf/materiel/LIT-0142`. À la lecture, l'app retrouve l'équipement dont le lien est identique, ou dont la référence termine le lien.

Bouton « Paramètres » en haut à droite :

- Écrire le lien sur une puce : l'app programme une puce vierge ou réinscriptible avec le lien de l'équipement.
- Lire une puce déjà programmée : le lien présent sur la puce est associé à l'équipement.
- Saisir le lien à la main, le copier, ou retirer la puce.
- Adresse des liens : le début commun des liens (par défaut l'adresse de la démo en ligne ; à remplacer par votre propre site).
- Tester une puce, effacer toutes les puces, rétablir les liens par défaut.

Les associations sont mémorisées sur l'appareil. Une puce lue hors de l'app ouvre son lien dans Safari ; avec l'adresse par défaut, la démo en ligne s'ouvre sur la fiche de l'équipement.

## Plan

Le plan dessiné montre où se trouve le matériel (dépôt ou domicile du bénéficiaire, adresses fictives). Dans l'app iPhone, « Zoomer » ouvre la vraie carte Apple Plans, zoomable jusqu'à l'adresse, avec l'itinéraire. Dans la démo en ligne, « Zoomer » ouvre Apple Plans dans le navigateur.

## Modifier l'interface

Modifier `index.html` à la racine, puis recopier dans le projet Xcode :

```bash
ios/sync-web.sh
```

Photos du matériel : Wikimedia Commons (auteurs et licences dans l'écran Parc, « Crédits photos »).
