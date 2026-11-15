# Tahiti Parc NFC — application iPhone (SwiftUI)

Application native pour l'App Store, reliée au serveur en ligne
`https://manaprocess.cloud/materiel/` (mêmes comptes, mêmes données que la version web).

## Ouvrir et lancer

1. Sur le Mac : `git pull`, puis ouvrir `ios/TahitiParcNFC/TahitiParcNFC.xcodeproj`.
2. Cible **TahitiParcNFC** › *Signing & Capabilities* : choisir votre **Team**
   (compte Apple Developer). Identifiant proposé : `cloud.manaprocess.tahitiparcnfc`
   (modifiable ; il doit être unique sur l'App Store).
3. Vérifier que la capacité **Near Field Communication Tag Reading** est présente
   (elle est déclarée dans `Config/TahitiParcNFC.entitlements`).
4. Brancher l'iPhone et lancer (⌘R). Le NFC ne fonctionne pas sur le simulateur.

iOS 17 minimum, iPhone, en portrait.

## Ce que fait l'application

| Écran | Équipe du parc | Pharmacie |
|---|---|---|
| Accueil | Taux d'occupation, revenu mensuel estimé, compteurs par état, alertes | Locations en cours, ordonnances à vérifier, alertes |
| Parc / Locations | Liste filtrable (état, type, recherche) | Ses locations uniquement |
| Scanner | Lecture de l'étiquette NFC → fiche + passage géolocalisé | Idem |
| Fiche équipement | Location, ordonnance, actions (prolonger, retour, désinfection, maintenance, panne, contrôle), position sur carte, photos horodatées, rentabilité, puce NFC, historique | Location, ordonnance, photos, historique |
| Facturation | Par mois et par pharmacie, export CSV | Sa facturation |
| Plus | Mot de passe, guides PDF, entretien, déconnexion | Mot de passe, guide pharmacie |

Fonctions natives : Core NFC (lecture et programmation des puces), CoreLocation
(position au scan et sur les photos), appareil photo (bandeau date/heure/position
incrusté), VisionKit (scan de l'ordonnance), MapKit, app Fichiers.

### Ordonnances

Aucune ordonnance n'est envoyée au serveur. Le scan (ou l'import d'une photo, PDF,
HEIC…) est converti en PDF et enregistré **dans le dossier choisi par la pharmacie**
via l'app Fichiers (serveur SMB, NAS, dossier partagé). « Voir l'ordonnance » relit
le fichier depuis ce dossier. En ligne, seule la vérification est enregistrée
(date, validité, n° interne, auteur).

## Publication sur l'App Store

- **Compte Apple Developer** (99 USD/an) au nom de ManaProcess.
- App Store Connect : créer l'app « Tahiti Parc NFC », catégorie *Médecine* ou
  *Économie et entreprise*.
- **Compte de démonstration pour Apple** : créer un compte `pharmacie` et un compte
  `equipe` de test (mot de passe définitif, pas provisoire) et les indiquer dans
  *App Review Information*, en précisant que le NFC nécessite une étiquette
  (joindre une vidéo de démonstration du scan).
- **Distribution conseillée** : l'application ne sert qu'aux clients de ManaProcess.
  Deux options :
  - *Distribution non répertoriée* (unlisted) : publique mais introuvable sans lien ;
  - *Apps personnalisées* via Apple Business Manager : réservée aux pharmacies clientes.
- Confidentialité (App Privacy) : position précise et photos, liées à l'utilisateur,
  pour le fonctionnement de l'app, sans pistage (voir `PrivacyInfo.xcprivacy`).
  Fournir l'URL d'une politique de confidentialité.
- Archive : *Product › Archive*, puis *Distribute App › App Store Connect*.

## Ouvrir l'app en scannant une puce, sans lancer l'app (optionnel)

Aujourd'hui, une puce scannée app fermée ouvre la version web dans Safari.
Pour qu'elle ouvre directement l'application (Universal Links), il faudra :
ajouter la capacité *Associated Domains* `applinks:manaprocess.cloud`, et publier
le fichier `/.well-known/apple-app-site-association` (avec votre Team ID) sur
manaprocess.cloud. L'app gère déjà ces liens (`onOpenURL` dans l'onglet Scanner).

## Organisation du code

```
TahitiParcNFC/
  App/       point d'entrée, aiguillage connexion / onglets
  Core/      client API (cookie de session), modèles, état, thème, formats (XPF, dates)
  Native/    NFC, localisation, appareil photo + bandeau horodaté
  Views/     écrans SwiftUI
Config/      Info.plist, droits NFC
```
