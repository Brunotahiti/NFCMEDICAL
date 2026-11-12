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

## Scan NFC

- Puce connue : la fiche de l'équipement s'ouvre.
- Puce inconnue : l'app propose de l'associer à un équipement ; l'association est mémorisée sur l'appareil.

## Plan

Le plan est un contour simplifié de Tahiti dessiné dans la page ; chaque équipement est placé au dépôt ou au domicile du bénéficiaire (adresses fictives). Le bouton « Plans » d'une fiche ouvre l'endroit dans Apple Plans.

## Modifier l'interface

Modifier `index.html` à la racine, puis recopier dans le projet Xcode :

```bash
ios/sync-web.sh
```

Photos du matériel : Wikimedia Commons (auteurs et licences dans l'écran Parc, « Crédits photos »).
