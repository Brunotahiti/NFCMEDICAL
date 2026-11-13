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

## Mise en ligne sur manaprocess.cloud

La démo est en ligne sur `https://manaprocess.cloud/materiel/` : une puce scannée sans l'app ouvre la fiche de l'équipement dans Safari (par exemple `…/materiel/LIT-0101`).

Sur le VPS, le projet Docker `mediparc-nfc` (fichier `deploy/docker-compose.yml`) lance un conteneur nginx derrière Traefik. À chaque démarrage, il télécharge ce dépôt (qui doit rester public), génère le site avec `deploy/build.sh` et le sert. Pour publier une nouvelle version : pousser sur la branche, puis redémarrer le projet `mediparc-nfc`.

## Icône

`icons/` contient l'icône (1024 px et tailles web) et sa source `icon-source.html`. Elle sert d'icône à l'app iPhone (Assets.xcassets) et à l'ajout sur l'écran d'accueil depuis Safari (nom « MédiParc »).

## Modifier l'interface

Modifier `index.html` à la racine, puis recopier dans le projet Xcode :

```bash
ios/sync-web.sh
```

Photos du matériel : Wikimedia Commons (auteurs et licences dans l'écran Parc, « Crédits photos »).
