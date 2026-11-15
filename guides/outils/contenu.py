"""Contenu des guides d'utilisation MédiParc NFC."""

def pharmacie(g):
    phone, crop, duo, steps, bullets, tip, warn, key, split, faq = (g[k] for k in ('phone','crop','duo','steps','bullets','tip','warn','key','split','faq'))
    ui = lambda t: f'<span class="ui">{t}</span>'
    ch = []
    ch.append(('Bienvenue sur votre portail', 'Ce que vous pouvez faire et ce que vous voyez',
      split('<p>Le portail MédiParc vous permet de suivre <b>en temps réel</b> le matériel médical que votre pharmacie a mis en location : lits, fauteuils, aérosols, tire-lait…</p>'
        + bullets('Voir toutes <b>vos</b> locations en cours, à renouveler et terminées.',
                  'Consulter la fiche de chaque matériel : bénéficiaire, dates, photos horodatées, historique.',
                  'Scanner, enregistrer et confirmer les <b>ordonnances</b>, sans qu\'elles quittent votre pharmacie.',
                  'Recevoir les <b>rappels</b> quand une ordonnance doit être renouvelée.',
                  'Suivre votre <b>facturation</b> mois par mois et l\'exporter.')
        + key('Confidentialité', 'Vous ne voyez que les locations de votre pharmacie. Aucune ordonnance n\'est stockée en ligne : elles restent sur le serveur de votre pharmacie.'),
        phone('p_home', 'Le tableau de bord de votre portail'))))
    ch.append(('Se connecter', 'Première connexion, mot de passe et raccourci sur le téléphone',
      split('<h3>Première connexion</h3>' + steps('Ouvrez <b>https://manaprocess.cloud/materiel/</b> sur votre téléphone, tablette ou ordinateur.',
                'Saisissez l\'<b>identifiant</b> et le <b>mot de passe provisoire</b> transmis par l\'équipe du parc.',
                'Choisissez votre propre mot de passe : <b>10 caractères au moins</b>, avec des lettres et des chiffres.',
                'Touchez ' + ui('Enregistrer') + ' : vous arrivez sur votre tableau de bord.')
        + warn('Mot de passe oublié', 'Contactez l\'équipe du parc : elle vous transmettra un nouveau mot de passe provisoire. Après 8 essais erronés, la connexion est bloquée 15 minutes.'),
        phone('p_login', 'L\'écran de connexion'))
      + '<h3>Installer le raccourci sur l\'écran d\'accueil</h3>'
      + bullets('<b>iPhone (Safari)</b> : bouton Partager, puis ' + ui('Sur l\'écran d\'accueil') + '. L\'icône MédiParc apparaît comme une application.',
                '<b>Android (Chrome)</b> : menu ⋮, puis ' + ui('Installer l\'application') + ' ou ' + ui('Ajouter à l\'écran d\'accueil') + '.',
                '<b>Ordinateur</b> : ajoutez l\'adresse à vos favoris. Chrome et Edge proposent aussi de l\'installer.')
      + tip('Restez connecté', 'La session reste ouverte 30 jours sur un appareil. Sur un poste partagé, pensez à vous déconnecter : menu ' + ui('Plus') + ' puis ' + ui('Se déconnecter') + '.')))
    ch.append(('Le tableau de bord', 'Tout ce qui demande votre attention, d\'un coup d\'œil',
      split('<p>Le tableau de bord résume votre parc locatif. Il est à jour à chaque scan d\'étiquette NFC.</p>'
        + bullets('<b>Le bandeau</b> : nombre d\'équipements en location et loyers par semaine.',
                  '<b>Les tuiles</b> : bénéficiaires équipés, locations à renouveler sous 14 jours, ordonnances à traiter, locations terminées. Touchez une tuile pour ouvrir le détail.',
                  '<b>À traiter</b> : la liste des actions, les plus urgentes en premier.')
        + '<table class="t"><tr><th>Étiquette</th><th>Signification</th></tr>'
        + '<tr><td><span class="tag t-c">Expirée</span></td><td>L\'ordonnance a expiré alors que le matériel est toujours chez le bénéficiaire.</td></tr>'
        + '<tr><td><span class="tag t-w">À renouveler</span></td><td>L\'ordonnance expire sous 14 jours, ou finit avant la fin de location prévue.</td></tr>'
        + '<tr><td><span class="tag t-w">Ordonnance</span></td><td>L\'ordonnance de cette location n\'a pas encore été confirmée.</td></tr>'
        + '<tr><td><span class="tag t-o">Retour</span></td><td>Retour du matériel prévu aujourd\'hui (ou en retard).</td></tr></table>'
        + tip('La cloche', 'La pastille rouge en haut de l\'écran indique le nombre d\'actions à traiter. Touchez-la pour les afficher.'),
        phone('p_home2', 'La liste « À traiter »'))))
    ch.append(('Vos locations', 'Contrats en cours, à renouveler et terminés',
      split(bullets('<b>Contrats en cours</b> : vos bénéficiaires équipés, avec pour chaque matériel la durée écoulée, la durée restante et une barre de progression.',
                    '<b>À renouveler</b> : les locations dont le retour est prévu dans les 14 jours.',
                    '<b>Terminés</b> : l\'historique de vos locations passées, avec leur montant.')
        + '<p>Le bouton entonnoir filtre les contrats par commune ; le bouton flèches change le tri (bénéficiaire, loyer, retour le plus proche).</p>'
        + tip('Ouvrir une fiche', 'Touchez une ligne pour ouvrir la fiche complète du matériel loué.'),
        phone('p_loc', 'L\'écran Locations'))))
    ch.append(('La fiche d\'une location', 'Toutes les informations d\'un matériel loué',
      split('<p>La fiche rassemble tout ce qui concerne un matériel :</p>'
        + bullets('<b>Durée</b> : loué depuis, encore combien de temps, date de retour prévue.',
                  '<b>Bénéficiaire</b> : emplacement, téléphone (touchez le numéro pour appeler), votre pharmacie.',
                  '<b>Dernier scan</b> : date, auteur et position lors de la dernière lecture de l\'étiquette NFC.',
                  '<b>Ordonnance</b> : vérification, validité et rappels (voir chapitre suivant).',
                  '<b>Photos horodatées</b> : l\'état du matériel à la livraison et au retour.',
                  '<b>Localisation</b> et <b>historique</b> complet de la location.'),
        phone('p_fiche', 'La fiche d\'un lit en location'))
      + '<h3>Photos horodatées du matériel</h3><p>L\'équipe du parc photographie le matériel à la livraison, au retour ou en cas de panne. La date, l\'heure, la référence, l\'auteur et la position sont incrustées sur chaque photo : elles font foi en cas de désaccord sur l\'état du matériel.</p>'
      + crop('p_photos', 'Les photos horodatées, visibles aussi dans l\'historique')))
    ch.append(('Les ordonnances', 'Scanner, enregistrer chez vous, confirmer et renouveler',
      key('Aucune ordonnance n\'est stockée en ligne', 'Le scan est préparé sur votre appareil puis enregistré <b>uniquement sur le serveur de votre pharmacie</b>. Le portail va le relire sur ce serveur local pour l\'afficher. En ligne, seule la vérification est enregistrée : date, validité, numéro interne et auteur.')
      + split('<h3>1. Scanner ou importer l\'ordonnance</h3>' + steps('Ouvrez la fiche de la location, section <b>Ordonnance</b>.',
                'Touchez ' + ui('Scanner') + ' pour photographier l\'ordonnance, ou ' + ui('Importer un fichier') + ' pour choisir un fichier existant (tout format : photo, PDF, TIFF…).',
                'Les photos sont transformées en PDF ; les autres fichiers sont conservés tels quels.')
        + '<h3>2. L\'enregistrer sur votre serveur</h3>' + bullets('<b>Ordinateur (Chrome ou Edge)</b> : ' + ui('Enregistrer dans le dossier de la pharmacie') + '. La première fois, choisissez le dossier des ordonnances sur votre serveur ; il est mémorisé sur ce poste.',
                '<b>iPhone, Android, application iPhone</b> : ' + ui('Enregistrer sur le serveur de la pharmacie') + ', puis « Enregistrer dans Fichiers » et le dossier de votre serveur.',
                '<b>Autre navigateur</b> : ' + ui('Télécharger le fichier') + ', puis rangez-le dans votre dossier.')
        + tip('Nom du fichier', 'Le fichier est nommé automatiquement : <b>Ordonnance_date_référence_initiales</b>. Ce nom est repris comme numéro interne de la vérification.'),
        phone('p_scan', 'L\'ordonnance prête à être enregistrée'))
      + split('<h3>3. Confirmer l\'ordonnance</h3>' + steps('Indiquez la <b>date de l\'ordonnance</b>.',
                'Indiquez jusqu\'à quand elle est <b>valable</b> : touchez 1, 3, 6 ou 12 mois, ou choisissez une date.',
                'Vérifiez le numéro interne (rempli automatiquement après un scan).',
                'Cochez la case <b>« La pharmacie détient l\'ordonnance originale… »</b> puis ' + ui('Enregistrer') + '.')
        + '<p>La location passe alors à <span class="tag t-o">Vérifiée</span>. Toute l\'équipe de votre pharmacie la voit, sur tous les postes.</p>',
        phone('p_presc', 'Confirmer l\'ordonnance et sa validité'), rev=True)
      + '<h3>4. Revoir une ordonnance</h3><p>' + ui('Voir l\'ordonnance') + ' retrouve le fichier de cette location dans le dossier de votre serveur et l\'affiche sur votre appareil. Sur téléphone, choisissez le fichier dans l\'application Fichiers. L\'appareil doit avoir accès au serveur de la pharmacie (réseau de l\'officine ou serveur connecté dans Fichiers).</p>'
      + '<h3>5. Renouveler une ordonnance</h3>'
      + split('<p>L\'application signale <span class="tag t-w">Nouvelle ordonnance à prévoir</span> 14 jours avant l\'expiration, ou quand une prolongation dépasse la validité, puis <span class="tag t-c">Ordonnance expirée</span>.</p>'
        + steps('Récupérez la nouvelle ordonnance auprès du bénéficiaire.', 'Scannez-la et enregistrez-la sur votre serveur.', 'Touchez ' + ui('Enregistrer la nouvelle ordonnance') + ' et indiquez sa date et sa validité.')
        + '<p>Le rappel disparaît aussitôt, et l\'historique garde la trace de chaque ordonnance vérifiée.</p>',
        crop('p_ordo', 'Une ordonnance expirée à renouveler'))))
    ch.append(('Les rappels par e-mail', 'Être prévenu sans ouvrir le portail',
      split('<p>Chaque matin, si quelque chose demande votre attention, vous recevez <b>un seul e-mail</b> récapitulatif :</p>'
        + bullets('ordonnances à confirmer (2 jours après le début d\'une location) ;',
                  'ordonnances à renouveler (14 jours puis 3 jours avant l\'expiration, ou plus courtes que la location) ;',
                  'ordonnances expirées.')
        + '<p>Chaque rappel n\'est envoyé qu\'une fois par étape. Le bénéficiaire n\'y apparaît que par ses initiales et sa commune ; le lien <b>Ouvrir la fiche</b> demande la connexion au portail.</p>'
        + '<h3>Changer l\'adresse de réception</h3>' + steps('Menu ' + ui('Plus') + ', puis ' + ui('E-mail des rappels') + '.', 'Saisissez une ou plusieurs adresses, séparées par une virgule.', 'Touchez ' + ui('Enregistrer') + '. Laissez vide pour ne plus recevoir de rappels.'),
        phone('p_mail', 'L\'adresse des rappels'))))
    ch.append(('La facturation', 'Vos montants de location, mois par mois',
      split('<p>L\'écran ' + ui('Facturation') + ' présente vos locations du mois, regroupées par pharmacie, avec pour chaque ligne la période, le nombre de jours, le tarif et le montant.</p>'
        + bullets('Changez de mois avec les flèches.', 'Le mois en cours est <b>prévisionnel</b> : les locations y sont comptées jusqu\'à la fin du mois.',
                  '<b>Calcul</b> : jours de location dans le mois × tarif hebdomadaire ÷ 7. Le jour du retour n\'est pas facturé.',
                  'La date de l\'ordonnance figure sur chaque ligne.')
        + tip('Exporter', ui('Télécharger (CSV)') + ' crée un fichier qui s\'ouvre dans Excel ; ' + ui('Copier pour un tableur') + ' permet de coller directement les lignes.'),
        phone('p_fact', 'La facturation du mois'))))
    ch.append(('Scanner une étiquette NFC', 'Retrouver un matériel en approchant le téléphone',
      '<p>Chaque matériel porte une étiquette NFC. La lire ouvre directement sa fiche.</p>'
      + '<table class="t"><tr><th>Appareil</th><th>Comment faire</th></tr>'
      + '<tr><td><b>iPhone</b></td><td>Approchez le haut de l\'iPhone de l\'étiquette : une notification propose d\'ouvrir la fiche. Avec l\'application MédiParc, utilisez ' + ui('+') + ' puis ' + ui('Scanner une puce NFC') + '.</td></tr>'
      + '<tr><td><b>Android</b></td><td>Dans Chrome, touchez ' + ui('+') + ' puis ' + ui('Scanner une puce NFC') + ' et approchez le dos du téléphone. Le NFC doit être activé dans les réglages.</td></tr>'
      + '<tr><td><b>Ordinateur</b></td><td>Pas de lecture NFC : saisissez la référence du matériel (par exemple LIT-0101).</td></tr></table>'
      + tip('Pourquoi scanner ?', 'Chaque scan enregistre la date, l\'auteur et la position du téléphone (si vous l\'autorisez). Vous suivez ainsi où et quand le matériel a été vu pour la dernière fois.')
      + '<p>Une étiquette qui ne correspond à aucune de vos locations affiche un message : le matériel n\'est pas visible avec votre compte.</p>'))
    ch.append(('Questions fréquentes', 'Et comment nous joindre',
      faq(('Je ne vois pas une location de ma pharmacie.', 'Elle a peut-être été enregistrée au nom d\'une autre pharmacie. Contactez l\'équipe du parc pour la corriger.'),
          ('Je n\'arrive pas à enregistrer dans le dossier du serveur.', 'Sur ordinateur, utilisez Chrome ou Edge et vérifiez que le poste a accès au serveur. Sinon, utilisez « Télécharger le fichier » et rangez-le à la main.'),
          ('« Voir l\'ordonnance » ne trouve rien.', 'Le fichier doit contenir la référence du matériel dans son nom (c\'est automatique avec « Scanner »). Vérifiez aussi que vous êtes dans le bon dossier : « Changer de dossier ».'),
          ('Puis-je envoyer l\'ordonnance à l\'équipe du parc ?', 'Ce n\'est pas nécessaire : seule sa vérification est utile au suivi. En cas de contrôle, l\'équipe vous demandera l\'ordonnance par son numéro interne.'),
          ('Je ne reçois plus les e-mails de rappel.', 'Vérifiez l\'adresse dans Plus › E-mail des rappels, et votre dossier de courriers indésirables.'),
          ('Plusieurs personnes de la pharmacie peuvent-elles se connecter ?', 'Oui : demandez à l\'équipe du parc un compte par personne. L\'historique indiquera qui a vérifié chaque ordonnance.'))
      + f'<div class="contact"><b>Besoin d\'aide ?</b><br>{g["CONTACT"]}<br>Du lundi au vendredi, de 8 h à 16 h (heure de Tahiti).</div>'))
    intro = ('<div class="intro"><div class="c"><b>À qui s\'adresse ce guide ?</b>Aux pharmacies clientes qui suivent leurs locations de matériel médical dans le portail MédiParc.</div>'
             '<div class="c"><b>Adresse du portail</b>https://manaprocess.cloud/materiel/<br>Identifiant et mot de passe fournis par l\'équipe du parc.</div></div>')
    return {'file': 'guide-pharmacie.pdf', 'footer': 'MédiParc NFC · Guide du portail pharmacie', 'intro': intro, 'chapters': ch,
            'cover': ('Guide d\'utilisation', 'Portail<br>pharmacie', 'Suivez vos locations de matériel médical, vos ordonnances et votre facturation, en toute confidentialité.',
                      'Pour les pharmacies clientes', [('p_home', 46), ('p_fiche', 46)])}


def administrateur(g):
    phone, crop, duo, steps, bullets, tip, warn, key, split, faq = (g[k] for k in ('phone','crop','duo','steps','bullets','tip','warn','key','split','faq'))
    ui = lambda t: f'<span class="ui">{t}</span>'
    ch = []
    ch.append(('Présentation et rôles', 'Qui fait quoi dans MédiParc',
      '<p>MédiParc NFC suit chaque équipement du parc de location grâce à une étiquette NFC : où il est, chez qui, depuis quand, dans quel état, et ce qu\'il rapporte.</p>'
      + '<table class="t"><tr><th>Rôle</th><th>Accès</th></tr>'
      + '<tr><td><b>Administrateur</b></td><td>Tout, y compris les comptes, les pharmacies, l\'adresse des liens NFC et les e-mails de rappel.</td></tr>'
      + '<tr><td><b>Équipe du parc</b></td><td>Parc, locations, entretien, étiquettes NFC, photos, rapports et facturation.</td></tr>'
      + '<tr><td><b>Pharmacie</b></td><td>Son portail uniquement : ses locations, ses bénéficiaires, ses ordonnances et sa facturation (guide séparé).</td></tr></table>'
      + duo('a_home', 'Le tableau de bord de l\'équipe', 'p_home', 'Le portail vu par une pharmacie')))
    ch.append(('Première connexion et sécurité', 'Adresse, mot de passe et bonnes pratiques',
      split(steps('Ouvrez <b>https://manaprocess.cloud/materiel/</b> (ou l\'application iPhone MédiParc).', 'Identifiant <b>admin</b> et mot de passe provisoire remis à l\'installation.',
                  'Choisissez votre mot de passe : 10 caractères au moins, lettres et chiffres. Le provisoire ne fonctionne plus ensuite.')
        + warn('Sécurité', 'Créez un compte nominatif pour chaque membre de l\'équipe plutôt que de partager le compte admin : l\'historique indiquera qui a fait quoi. Après 8 essais erronés, la connexion est bloquée 15 minutes.')
        + tip('Sur le téléphone', 'iPhone : application MédiParc (lecture NFC), ou Safari › Partager › Sur l\'écran d\'accueil. Android : Chrome, menu ⋮ › Installer l\'application.'),
        phone('a_pwd', 'Choix du mot de passe à la première connexion'))))
    ch.append(('Le tableau de bord', 'L\'état du parc et les actions du jour',
      split(bullets('<b>Taux d\'occupation</b> et revenus de location par semaine ; touchez un état (En location, Disponible…) pour voir la liste.',
                    '<b>Tuiles</b> : revenus, équipements, actions à traiter, maintenance.',
                    '<b>À traiter</b> : ordonnances expirées ou à renouveler, contrôles de sécurité en retard, retours du jour, désinfections en attente.',
                    '<b>Aperçu du parc</b> : courbe d\'occupation (7 ou 30 jours) et répartition par état.',
                    '<b>Prêt à louer</b> et <b>Où est le matériel</b>.')
        + tip('Le bouton +', 'Actions rapides : scanner une puce, mettre en location, enregistrer un retour, valider une désinfection.'),
        phone('a_home2', 'À traiter et aperçu du parc'))))
    ch.append(('Le parc matériel', 'Liste, plan, statistiques et maintenance',
      split(bullets('<b>Liste</b> : tuiles par état (touchez pour filtrer), recherche par nom, référence ou bénéficiaire, filtres et favoris (cœur).',
                    'Le menu <b>⋮</b> d\'une carte : ouvrir la fiche, voir sur le plan, favori, écrire la puce.',
                    '<b>Plan</b> : où se trouve chaque matériel (dépôt ou domicile), avec zoom jusqu\'à l\'adresse et itinéraire dans l\'application iPhone.',
                    '<b>Statistiques</b> : répartition, occupation, rentabilité.',
                    '<b>Maintenance</b> : désinfections, pannes, contrôles.'),
        phone('a_parc', 'Le parc en liste'))
      + duo('a_plan', 'Vue Plan', 'a_stats', 'Vue Statistiques')))
    ch.append(('La fiche d\'un équipement', 'Le cycle de vie : location, retour, désinfection, maintenance',
      split('<p>La fiche affiche l\'état, le lien de la puce NFC, la durée de location, le bénéficiaire et son téléphone, la pharmacie, le prix, le prochain contrôle, le dernier scan, la rentabilité, les photos, la localisation et l\'historique.</p>'
        + '<h3>Les actions selon l\'état</h3><table class="t"><tr><th>État</th><th>Bouton</th><th>Résultat</th></tr>'
        + '<tr><td>Disponible</td><td>' + ui('Mettre en location') + '</td><td>En location</td></tr>'
        + '<tr><td>En location</td><td>' + ui('Enregistrer le retour') + '</td><td>Désinfection</td></tr>'
        + '<tr><td>Désinfection</td><td>' + ui('Valider la désinfection') + '</td><td>Disponible</td></tr>'
        + '<tr><td>Maintenance</td><td>' + ui('Clôturer la maintenance') + '</td><td>Disponible</td></tr>'
        + '<tr><td>Tous</td><td>' + ui('Signaler une panne') + '</td><td>Maintenance</td></tr></table>'
        + tip('Prolonger', 'Sur une location en cours, ' + ui('+ 1 semaine') + ' repousse la date de retour. Si la nouvelle date dépasse la validité de l\'ordonnance, un rappel apparaît.'),
        phone('a_fiche_loc', 'Fiche d\'un lit en location'))))
    ch.append(('Mettre en location', 'Durée, pharmacie et bénéficiaire',
      split(steps('Ouvrez un équipement <b>Disponible</b> et touchez ' + ui('Mettre en location') + '.', 'Choisissez la <b>durée prévue</b> : 1, 2, 4 semaines ou 3 mois.',
                  'Choisissez la <b>pharmacie</b> qui délivre la location.', 'Touchez le <b>bénéficiaire</b>, ou ' + ui('Nouveau bénéficiaire') + ' pour le créer.')
        + '<p>La location démarre aussitôt. La pharmacie la voit dans son portail et doit confirmer l\'ordonnance.</p>'
        + warn('Aucune information médicale', 'Un bénéficiaire = nom, commune, adresse et téléphone, chiffrés dans la base. Ne saisissez jamais de pathologie, de motif ou de prescripteur.'),
        phone('a_assign', 'Choix de la durée, de la pharmacie et du bénéficiaire'))
      + duo('a_newpat', 'Nouveau bénéficiaire', 'a_fiche_dispo', 'Un équipement disponible')))
    ch.append(('Les étiquettes NFC', 'Programmer, associer et scanner',
      '<p>Chaque étiquette contient un <b>lien</b> propre à l\'équipement, par exemple <b>https://manaprocess.cloud/materiel/LIT-0101</b>. Lue par un téléphone, elle ouvre la fiche.</p>'
      + split('<h3>Programmer une étiquette</h3>' + steps('Menu ' + ui('Plus') + ' › ' + ui('Paramètres') + ', ou ' + ui('Écrire le lien sur une puce') + ' dans la fiche.',
                'Touchez l\'équipement, puis ' + ui('Écrire le lien sur une puce') + '.',
                'Approchez l\'étiquette du téléphone (haut de l\'iPhone, dos d\'un Android) jusqu\'à la confirmation.')
        + bullets(ui('Lire une puce déjà programmée') + ' : associe une étiquette existante à l\'équipement.',
                  'Une étiquette déjà utilisée est automatiquement retirée de l\'ancien équipement.',
                  'Le compteur en haut indique les équipements avec et sans puce.')
        + tip('Pose', 'Utilisez des étiquettes anti-métal, sur une surface propre et sèche, à un endroit protégé des chocs et facile à atteindre. Testez chaque étiquette après la pose avec ' + ui('Tester une puce') + '.'),
        phone('a_settings', 'Paramètres › Puces NFC'))
      + '<h3>Scanner</h3><table class="t"><tr><th>Appareil</th><th>Lecture et écriture</th></tr>'
      + '<tr><td>Application iPhone MédiParc</td><td>' + ui('+') + ' › ' + ui('Scanner une puce NFC') + ' (lecture et écriture).</td></tr>'
      + '<tr><td>Android, Chrome</td><td>Même bouton, directement dans le navigateur (lecture et écriture).</td></tr>'
      + '<tr><td>iPhone sans l\'application</td><td>Approcher l\'étiquette ouvre la fiche dans Safari (lecture seule).</td></tr></table>'
      + key('Géolocalisation', 'Chaque scan enregistre la date, l\'auteur et la position du téléphone si elle est autorisée : la fiche affiche le « Dernier scan » avec un lien vers la carte.')))
    ch.append(('Les photos horodatées', 'Prouver l\'état du matériel',
      split(steps('Dans la fiche, touchez ' + ui('Prendre une photo horodatée') + '.', 'Choisissez le type : <b>Livraison</b>, <b>Retour</b>, <b>État</b> ou <b>Panne</b>.', 'Prenez la photo.')
        + bullets('La date, l\'heure à la seconde, la référence, l\'auteur, la position et le type sont <b>incrustés sur l\'image</b>.',
                  'Le serveur enregistre en plus sa propre heure, qui fait foi.',
                  'Les photos apparaissent dans la fiche et, en vignette, dans l\'historique.',
                  'La pharmacie voit les photos prises pendant ses locations.')
        + tip('Bonne pratique', 'Photographiez le matériel à chaque livraison et à chaque retour : en cas de casse, la comparaison est immédiate. Ne photographiez que le matériel, jamais le bénéficiaire ni son intérieur.'),
        phone('a_photo_sheet', 'Choix du type de photo'))
      + crop('a_photos', 'Les photos dans la fiche de l\'équipement')))
    ch.append(('Locations et renouvellements', 'Suivre et prolonger les contrats',
      split(bullets('<b>Contrats en cours</b> : regroupés par bénéficiaire, avec la pharmacie de chaque matériel ; filtres par pharmacie et commune, tri par bénéficiaire, loyer ou retour.',
                    'Le menu <b>⋮</b> d\'un bénéficiaire : voir sur le plan, prolonger tous ses équipements d\'une semaine.',
                    '<b>À renouveler</b> : retours prévus sous 14 jours, avec ' + ui('+ 1 sem.') + ' pour prolonger.',
                    '<b>Terminés</b> : l\'historique avec montants.'),
        phone('a_renew', 'Les locations à renouveler'))))
    ch.append(('Entretien', 'Désinfection, maintenance et contrôles',
      split(bullets('<b>Contrôles à venir</b> et <b>actions en cours</b> : touchez une tuile pour aller à la section.',
                    '<b>À désinfecter</b> : le matériel revenu de location. Validez la désinfection dans sa fiche pour le remettre en stock.',
                    '<b>En maintenance</b> : les pannes signalées.',
                    '<b>Prochains contrôles</b> : contrôles de sécurité sur 7 ou 30 jours ; les retards apparaissent en rouge sur le tableau de bord.')
        + key('Démarche qualité', 'L\'historique daté de chaque équipement (livraisons, retours, désinfections, pannes, scans géolocalisés, photos) sert d\'appui à une démarche qualité de type ISO 9001.'),
        phone('a_ent', 'L\'écran Entretien'))))
    ch.append(('Rapports, rentabilité et exports', 'Piloter le parc',
      split(bullets('<b>Vue d\'ensemble</b> : loyers encaissés depuis l\'achat, investissement, part amortie, revenu moyen par équipement, courbe d\'occupation (7 jours, 30 jours, 12 mois).',
                    '<b>Rentabilité</b> : chaque équipement, de son prix d\'achat aux loyers encaissés.',
                    '<b>Utilisation</b> : jours de location cumulés par équipement.',
                    '<b>Activité</b> : le journal des derniers événements.',
                    '<b>Exports</b> : inventaire, contrats en cours, rentabilité, copiés au format CSV pour un tableur.'),
        phone('a_rap', 'Rapports · Vue d\'ensemble'))))
    ch.append(('Facturation', 'Préparer les factures des pharmacies',
      split(steps('Menu ' + ui('Rapports') + ' › ' + ui('Facturation') + ', ou ' + ui('Plus') + ' › ' + ui('Facturation') + '.', 'Choisissez le mois avec les flèches, et éventuellement une pharmacie.',
                  'Vérifiez les lignes : bénéficiaire, référence, période, jours, tarif, montant, date d\'ordonnance.',
                  ui('Télécharger (CSV)') + ' pour Excel ou votre logiciel de facturation.')
        + '<p><b>Calcul</b> : jours de location dans le mois × tarif hebdomadaire ÷ 7, le jour du retour n\'étant pas facturé. Le mois en cours est prévisionnel. Une location dont l\'ordonnance n\'est pas vérifiée est signalée « Ordonnance non vérifiée ».</p>',
        phone('a_fact', 'La facturation du mois'))))
    ch.append(('Comptes et pharmacies', 'Donner et retirer les accès',
      split('<h3>Créer un compte</h3>' + steps('Menu ' + ui('Plus') + ' › ' + ui('Comptes et pharmacies') + ' › ' + ui('Nouveau compte') + '.',
                'Saisissez le nom affiché et l\'identifiant (minuscules, chiffres, point, tiret).',
                'Choisissez le rôle et, pour un compte pharmacie, la pharmacie.',
                'Touchez ' + ui('Créer le compte') + ', puis ' + ui('Copier') + ' pour transmettre l\'adresse, l\'identifiant et le mot de passe provisoire.')
        + warn('Mot de passe provisoire', 'Il n\'est affiché qu\'une fois. Transmettez-le par un canal sûr ; la personne choisira le sien à la première connexion.')
        + '<h3>Gérer les comptes</h3>' + bullets('Touchez un compte pour <b>réinitialiser son mot de passe</b> ou le <b>désactiver</b> (déconnexion immédiate).',
                ui('Nouvelle pharmacie') + ' ajoute une pharmacie cliente ; touchez une pharmacie pour saisir son adresse e-mail de rappel.'),
        phone('a_newuser', 'Création d\'un compte pharmacie'))
      + duo('a_accounts', 'Comptes et pharmacies', 'a_newuser_pw', 'Les accès à transmettre')))
    ch.append(('E-mails de rappel', 'Prévenir automatiquement les pharmacies',
      split('<p>Chaque jour à l\'heure choisie, chaque pharmacie reçoit un e-mail s\'il y a du nouveau : ordonnance à confirmer, à renouveler (14 puis 3 jours avant), plus courte que la location, expirée. Chaque rappel n\'est envoyé qu\'une fois par étape.</p>'
        + bullets('<b>Envoi automatique</b> : activer ou désactiver.', '<b>Heure d\'envoi</b> : 6, 7, 8 ou 9 h (heure de Tahiti).',
                  ui('Voir les rappels en attente') + ' : aperçu de ce qui partira.', ui('Envoyer un e-mail de test') + ' et ' + ui('Envoyer les rappels maintenant') + '.',
                  'Le compte rendu du dernier envoi s\'affiche en bas.')
        + tip('Adresses', 'Renseignez l\'adresse de chaque pharmacie (plusieurs possibles). Une pharmacie sans adresse ne reçoit rien ; elle peut aussi saisir la sienne dans son portail.')
        + warn('Service d\'envoi', 'L\'envoi passe par un service de messagerie (Resend, Brevo ou SMTP) configuré sur le serveur. Tant qu\'il ne l\'est pas, la section affiche « À configurer ».'),
        crop('a_mail', 'Réglages des e-mails de rappel'))))
    ch.append(('Ordonnances et protection des données', 'Les règles intégrées à l\'application',
      key('Aucune ordonnance n\'est stockée en ligne', 'Les pharmacies scannent ou importent l\'ordonnance ; le fichier est enregistré uniquement sur leur propre serveur et relu depuis ce serveur local. MédiParc n\'enregistre que la vérification : date, validité, numéro interne, auteur.')
      + '<table class="t"><tr><th>Règle</th><th>Application</th></tr>'
      + '<tr><td>Pas de donnée médicale</td><td>Ni ordonnance, ni pathologie, ni motif, ni prescripteur. Un bénéficiaire = nom, adresse, commune, téléphone.</td></tr>'
      + '<tr><td>Chiffrement</td><td>Nom, adresse et téléphone chiffrés en AES-256 dans la base et ses sauvegardes ; connexion HTTPS.</td></tr>'
      + '<tr><td>Cloisonnement</td><td>Une pharmacie ne voit jamais les données d\'une autre, même dans l\'historique d\'un équipement.</td></tr>'
      + '<tr><td>Conservation</td><td>Anonymisation automatique d\'un bénéficiaire 3 ans après la fin de sa dernière location ; les positions de scan et photos liées sont effacées. Les montants restent pour la comptabilité.</td></tr>'
      + '<tr><td>E-mails</td><td>Le bénéficiaire n\'apparaît que par ses initiales et sa commune.</td></tr></table>'
      + warn('À prévoir de votre côté', 'Désigner un référent pour la protection des données et tenir le registre des traitements. Informer les bénéficiaires de l\'utilisation de leurs coordonnées pour le suivi du matériel.')))
    ch.append(('Sauvegardes et bonnes pratiques', 'Pour un parc fiable au quotidien',
      bullets('<b>Sauvegarde automatique</b> de la base chaque jour sur le serveur, conservée 14 jours.',
              '<b>Clé de chiffrement</b> : conservée dans les variables du serveur (DATA_KEY). Gardez-en une copie en lieu sûr : sans elle, les noms des bénéficiaires ne peuvent plus être lus.',
              '<b>Un compte par personne</b> : désactivez le compte d\'un salarié qui quitte l\'entreprise.',
              '<b>Scanner à chaque mouvement</b> : livraison, retour, passage au dépôt. La position du dernier scan devient fiable.',
              '<b>Photographier</b> à la livraison et au retour.',
              '<b>Valider les désinfections</b> sans attendre : le matériel redevient disponible à la location.',
              '<b>Traiter « À traiter » chaque jour</b> : ordonnances, retours, contrôles en retard.')
      + f'<div class="contact"><b>Assistance ManaProcess</b><br>{g["CONTACT"]}<br>Du lundi au vendredi, de 8 h à 16 h (heure de Tahiti). Panne bloquante traitée en priorité.</div>'))
    ch.append(('Questions fréquentes', 'Les situations courantes',
      faq(('Une étiquette ne se lit pas.', 'Vérifiez que le NFC est activé (Android), retirez une éventuelle coque métallique, approchez lentement le haut de l\'iPhone ou le dos de l\'Android. Si elle reste illisible, posez une étiquette de réserve et programmez-la.'),
          ('Une étiquette ouvre le mauvais équipement.', 'Paramètres › touchez le bon équipement › Lire une puce déjà programmée : l\'étiquette est réattribuée et retirée de l\'ancien.'),
          ('Un bénéficiaire a déménagé.', 'Créez-le à nouveau avec la bonne adresse lors de la prochaine location ; l\'ancienne fiche sera anonymisée au bout de 3 ans.'),
          ('Une pharmacie a oublié son mot de passe.', 'Comptes et pharmacies › touchez son compte › Réinitialiser le mot de passe, puis transmettez le mot de passe provisoire.'),
          ('Les e-mails de rappel ne partent pas.', 'Vérifiez la section E-mails de rappel : service configuré, envoi activé, adresse de la pharmacie renseignée. Le compte rendu du dernier envoi indique les erreurs.'),
          ('Le montant d\'une facture semble faux.', 'Vérifiez les dates de début et de retour dans la fiche : le montant suit les jours de location réels dans le mois.'))))
    intro = ('<div class="intro"><div class="c"><b>À qui s\'adresse ce guide ?</b>À l\'administrateur et à l\'équipe du parc : gestionnaires, livreurs, techniciens.</div>'
             '<div class="c"><b>Adresse de l\'application</b>https://manaprocess.cloud/materiel/<br>Application iPhone MédiParc pour la lecture NFC.</div></div>')
    return {'file': 'guide-administrateur.pdf', 'footer': 'MédiParc NFC · Guide administrateur et équipe du parc', 'intro': intro, 'chapters': ch,
            'cover': ('Guide d\'utilisation', 'Administrateur<br>et équipe du parc', 'Gérez le parc de matériel médical en location : étiquettes NFC, locations, entretien, facturation, comptes et pharmacies.',
                      'Pour l\'administrateur et l\'équipe du parc', [('a_home', 46), ('a_fiche_loc', 46)])}
