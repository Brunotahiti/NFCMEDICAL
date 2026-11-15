"""Contenu des guides d'utilisation MédiParc NFC : pharmacie (ordinateur), grossiste (ordinateur), technicien (téléphone)."""


def _h(g):
    return {k: g[k] for k in ('phone', 'crop', 'duo', 'steps', 'bullets', 'tip', 'warn', 'key', 'split', 'faq', 'desk', 'win', 'annot', 'legend')}


def ui(t):
    return f'<span class="ui">{t}</span>'


def _tags(rows):
    return ('<table class="t"><tr><th>Étiquette</th><th>Signification</th></tr>'
            + ''.join(f'<tr><td><span class="tag {c}">{a}</span></td><td>{b}</td></tr>' for a, c, b in rows) + '</table>')


REQ_STATES = [('Nouvelle', 't-w', 'La demande est arrivée chez le grossiste, elle n\'est pas encore traitée.'),
              ('Planifiée', 't-o', 'Une date de passage est fixée. Elle est indiquée sur la demande et vous est envoyée par e-mail.'),
              ('Effectuée', 't-o', 'La livraison, la reprise, la prolongation ou l\'intervention est faite. La location est à jour.'),
              ('Refusée', 't-c', 'Le grossiste ne peut pas donner suite ; le motif est indiqué dans la réponse.'),
              ('Annulée', 't-w', 'La demande a été annulée par la pharmacie avant d\'être traitée.')]


# --------------------------------------------------------------------------------------------
def pharmacie(g):
    h = _h(g); steps, bullets, tip, warn, key, split, faq, desk, win, crop = (h[k] for k in ('steps', 'bullets', 'tip', 'warn', 'key', 'split', 'faq', 'desk', 'win', 'crop'))
    ch = []
    ch.append(('Bienvenue sur votre portail', 'Ce que vous pouvez faire depuis l\'ordinateur de l\'officine',
      '<p>Le portail MédiParc relie votre pharmacie au grossiste qui loue le matériel médical : lits, fauteuils, lève-personnes, aérosols, tire-lait… Depuis l\'ordinateur de l\'officine, vous <b>demandez</b> le matériel, vous <b>suivez</b> chaque location et vous <b>gérez les ordonnances</b> sans qu\'elles quittent votre pharmacie.</p>'
      + desk('p_home', 'Le tableau de bord de la pharmacie, sur ordinateur')
      + bullets('<b>Demander</b> une location, une reprise, une prolongation, ou signaler un problème, en quelques clics.',
                '<b>Suivre</b> vos demandes (nouvelle, planifiée, effectuée) et toutes vos locations en cours.',
                '<b>Vérifier les ordonnances</b> : scan enregistré sur le serveur de la pharmacie, rappels avant expiration.',
                '<b>Contrôler la facturation</b> de chaque mois et l\'exporter vers votre tableur.')
      + key('Confidentialité', 'Vous ne voyez que les bénéficiaires et le matériel de votre pharmacie. <b>Aucune ordonnance n\'est stockée en ligne</b> : seule sa vérification (date, validité, numéro interne) est enregistrée. Aucune information médicale n\'est demandée.')))
    ch.append(('Se connecter', 'Adresse, première connexion et mot de passe',
      split('<h3>Première connexion</h3>' + steps('Ouvrez <b>https://manaprocess.cloud/materiel/</b> dans Chrome, Edge, Safari ou Firefox.',
                'Saisissez l\'<b>identifiant</b> et le <b>mot de passe provisoire</b> transmis par le grossiste.',
                'Choisissez votre mot de passe : <b>10 caractères au moins</b>, avec des lettres et des chiffres.',
                'Cliquez sur ' + ui('Enregistrer') + ' : le tableau de bord s\'affiche.')
        + tip('Ajoutez le portail aux favoris', 'Dans Chrome ou Edge, vous pouvez aussi l\'<b>installer</b> (icône d\'installation dans la barre d\'adresse) : il s\'ouvre alors comme un logiciel, avec son icône sur le bureau.')
        + warn('Poste partagé', 'La session reste ouverte 30 jours. Sur un poste utilisé par plusieurs personnes, déconnectez-vous en fin de journée : menu ' + ui('Plus') + ' › ' + ui('Se déconnecter') + '. Après 8 essais erronés, la connexion est bloquée 15 minutes.'),
        win('p_pwd', 'Choix du mot de passe à la première connexion'), wide=True)
      + tip('Un compte par personne', 'Demandez au grossiste un identifiant pour chaque membre de l\'équipe officinale : l\'historique indiquera qui a fait chaque demande et chaque vérification d\'ordonnance.')))
    ch.append(('L\'écran principal', 'Le menu, la barre du haut et le tableau de bord',
      h['annot']('p_home', [(16.3, 12.2), (16.3, 25.1), (16.3, 95.1), (88.2, 3.6), (95.2, 2.0), (21.6, 23.4), (21.6, 41.4), (21.6, 58.6)], 'Les repères de l\'écran principal, sur ordinateur')
      + h['legend'](('Nouvelle demande', 'Location, reprise, prolongation ou problème.'),
                    ('Accueil, Locations, Facturation', 'Les trois écrans du portail.'),
                    ('Plus', 'Catalogue, e-mails, guide, mot de passe, déconnexion.'),
                    ('Recherche', 'Retrouver un bénéficiaire ou un matériel.'),
                    ('Cloche', 'Le nombre d\'actions à traiter.'),
                    ('Bandeau', 'Équipements en location et loyers par semaine.'),
                    ('Tuiles', 'Bénéficiaires, fins sous 14 jours, ordonnances, demandes.'),
                    ('Nouvelle demande', 'Les quatre demandes, directement depuis l\'accueil.'))
      + split('<h3>Le tableau de bord</h3>' + bullets('<b>Le bandeau</b> : nombre d\'équipements en location et loyers par semaine.',
                '<b>Les tuiles</b> : bénéficiaires équipés, fins de location sous 14 jours, ordonnances à traiter, demandes en cours. Cliquez sur une tuile pour ouvrir le détail.',
                '<b>À traiter</b> : les actions urgentes en premier (ordonnance expirée, retour en retard…).')
        + _tags([('Expirée', 't-c', 'L\'ordonnance a expiré alors que le matériel est encore chez le bénéficiaire.'),
                 ('À renouveler', 't-w', 'L\'ordonnance expire sous 14 jours, ou avant la fin de location prévue.'),
                 ('Ordonnance', 't-w', 'L\'ordonnance de cette location n\'a pas encore été vérifiée.'),
                 ('Retour', 't-o', 'Le retour du matériel est prévu aujourd\'hui, ou il est en retard.')]),
        desk('p_home2', 'La liste « À traiter »', small=False), wide=True)))
    ch.append(('Demander une location', 'Du matériel pour un nouveau bénéficiaire, en moins d\'une minute',
      split(steps('Cliquez sur ' + ui('Nouvelle demande') + ' (en haut du menu) puis ' + ui('Location') + ', ou sur la tuile <b>Location</b> de l\'accueil.',
                  '<b>Matériel</b> : choisissez le produit dans la liste. « Sur demande » signifie qu\'aucune unité n\'est libre aujourd\'hui : le grossiste vous proposera une date ou un autre modèle.',
                  '<b>Bénéficiaire</b> : choisissez-le dans la liste, ou cliquez sur ' + ui('Nouveau bénéficiaire') + ' (voir ci-dessous).',
                  '<b>Durée</b> : 1 semaine, 2 semaines, 4 semaines ou 3 mois. Elle pourra être prolongée.',
                  '<b>Livraison souhaitée le</b> : aujourd\'hui au plus tôt, dans les 4 mois au plus tard.',
                  '<b>Précisions</b> (facultatif) : accès, horaires, personne à prévenir.',
                  'Cliquez sur ' + ui('Envoyer la demande') + '. Elle apparaît aussitôt chez le grossiste, et dans vos demandes avec l\'état <span class="tag t-w">Nouvelle</span>.')
        + warn('Aucune information médicale', 'Ni pathologie, ni traitement, ni motif de la prescription dans les précisions : ce champ sert uniquement à la livraison. L\'ordonnance reste dans votre pharmacie.'),
        win('p_req_loc', 'Le formulaire de demande de location'), wide=True)
      + split('<h3>Créer un bénéficiaire</h3>' + steps('Dans le formulaire, cliquez sur ' + ui('Nouveau bénéficiaire') + '.',
                'Saisissez le <b>nom et prénom</b>, la <b>commune</b>, l\'<b>adresse</b> (PK, quartier, servitude) et le <b>téléphone</b>.',
                'Cliquez sur ' + ui('Ajouter') + ' : vous revenez à la demande, le bénéficiaire déjà choisi.')
        + key('Données protégées', 'Seuls le nom, l\'adresse, la commune et le téléphone sont enregistrés, <b>chiffrés</b> sur le serveur. Ils sont anonymisés 3 ans après la dernière location.'),
        win('p_newpat', 'Ajout d\'un bénéficiaire'), rev=True, wide=True)
      + split('<h3>Consulter le catalogue</h3><p>Menu ' + ui('Plus') + ' › ' + ui('Catalogue') + ', ou le lien <b>Catalogue</b> au-dessus des tuiles de demande : tout le matériel proposé, avec son tarif à la semaine et sa disponibilité. Cliquez sur un produit pour le demander directement.</p>',
        win('p_cat', 'Le catalogue et ses tarifs'), wide=True)))
    ch.append(('Reprise, prolongation, problème', 'Les demandes sur un matériel déjà loué',
      '<p>Ces trois demandes concernent un matériel <b>déjà chez un bénéficiaire</b>. Le plus simple est de les faire depuis sa fiche : ouvrez-la (Locations, ou recherche avec la loupe), les boutons sont en bas de la fiche.</p>'
      + desk('p_fiche_actions', 'La fiche d\'un matériel loué, avec les boutons de demande en bas')
      + '<table class="t"><tr><th>Demande</th><th>Quand l\'utiliser</th><th>Ce que vous indiquez</th></tr>'
      + '<tr><td><b>Prolongation</b></td><td>Le bénéficiaire a encore besoin du matériel après la date de retour prévue.</td><td>La durée supplémentaire : 1, 2, 4 semaines ou 3 mois.</td></tr>'
      + '<tr><td><b>Reprise</b></td><td>Le matériel n\'est plus utile (fin de traitement, hospitalisation, déménagement…).</td><td>La date souhaitée pour la reprise.</td></tr>'
      + '<tr><td><b>Problème</b></td><td>Le matériel ne fonctionne plus, fait du bruit, est abîmé ou sa batterie ne tient plus.</td><td>La nature du problème et une courte description.</td></tr></table>'
      + '<div class="duo">' + win('p_req_prol', 'Demande de prolongation') + win('p_req_pb', 'Signalement d\'un problème') + '</div>'
      + tip('Une seule demande à la fois', 'Tant qu\'une demande du même type est en cours pour ce matériel, le bouton disparaît de la fiche : la demande en cours s\'affiche à sa place, dans la section « Demandes en cours ».')
      + warn('Urgence', 'Pour un matériel dangereux (lit bloqué, fumée, chute), demandez au bénéficiaire de ne plus l\'utiliser et appelez directement le grossiste, en plus du signalement.')))
    ch.append(('Suivre vos demandes', 'Savoir où en est chaque demande',
      split('<p>Toutes vos demandes se trouvent dans ' + ui('Locations') + ' › <b>Demandes</b>. Les demandes en cours apparaissent aussi sur l\'accueil.</p>'
        + _tags(REQ_STATES)
        + bullets('Cliquez sur une demande pour voir son détail : matériel, bénéficiaire, dates, votre message et la <b>réponse du grossiste</b>.',
                  'L\'onglet <b>Historique</b> garde les demandes clôturées des 4 derniers mois.',
                  'Une demande pas encore effectuée peut être annulée : ' + ui('Annuler la demande') + '.'),
        win('p_req_detail', 'Le détail d\'une demande'), wide=True)
      + desk('p_dem', 'Locations › Demandes : toutes vos demandes et leur état')
      + tip('Prévenu par e-mail', 'Si une adresse est enregistrée (chapitre 10), vous recevez un e-mail quand une demande est planifiée, effectuée ou refusée. Le bénéficiaire n\'y figure que par ses initiales.')))
    ch.append(('Vos locations', 'Contrats en cours, à renouveler et terminés',
      desk('p_loc', 'Les contrats en cours, regroupés par bénéficiaire')
      + bullets('<b>Contrats en cours</b> : chaque bénéficiaire avec son matériel, la durée écoulée, la durée restante et une barre de progression.',
                '<b>À renouveler</b> : les locations dont la fin est prévue dans les 14 jours. C\'est le bon moment pour demander une prolongation ou une reprise.',
                '<b>Demandes</b> : vos demandes (chapitre précédent).',
                '<b>Terminés</b> : l\'historique de vos locations passées, avec leur montant.')
      + tip('Filtrer et trier', 'Le bouton entonnoir filtre par commune ; le bouton flèches change le tri (bénéficiaire, loyer, fin la plus proche). Cliquez sur un matériel pour ouvrir sa fiche.')))
    ch.append(('La fiche d\'un matériel', 'Tout ce qui concerne une location, au même endroit',
      desk('p_fiche', 'La fiche s\'ouvre à droite de l\'écran ; la flèche en haut à gauche la referme')
      + split(bullets('<b>Durée</b> : loué depuis, encore combien de temps, date de retour prévue.',
                      '<b>Bénéficiaire</b> : emplacement, téléphone, votre pharmacie.',
                      '<b>Dernier scan</b> : date, technicien et position lors de la dernière lecture de l\'étiquette NFC du matériel.',
                      '<b>Demandes en cours</b>, <b>Ordonnance</b> (chapitre suivant) et <b>photos horodatées</b>.',
                      '<b>Historique</b> : livraison, prolongations, vérifications d\'ordonnance, photos, retour.')
        + '<h3>Photos horodatées</h3><p>Le technicien photographie le matériel à la livraison, au retour ou en cas de panne. La date, l\'heure, la référence, l\'auteur et la position sont incrustées : elles font foi sur l\'état du matériel. Cliquez sur une photo pour l\'agrandir.</p>',
        crop('p_photos', 'Les photos horodatées du matériel'), wide=True)))
    ch.append(('Les ordonnances', 'Scanner, enregistrer chez vous, vérifier et renouveler',
      key('Aucune ordonnance n\'est stockée en ligne', 'Le scan est préparé sur votre ordinateur puis enregistré <b>uniquement dans le dossier des ordonnances de votre pharmacie</b> (serveur, NAS ou dossier partagé). Le portail relit ce dossier pour l\'afficher. En ligne, seule la vérification est enregistrée : date, validité, numéro interne et auteur.')
      + split('<h3>1. Scanner ou importer l\'ordonnance</h3>' + steps('Ouvrez la fiche de la location, section <b>Ordonnance</b>.',
                ui('Scanner') + ' : choisissez l\'image produite par votre scanner ou la webcam. ' + ui('Importer un fichier') + ' : tout format (photo, PDF, TIFF…).',
                'Les images sont converties en PDF ; les PDF sont conservés tels quels.')
        + '<h3>2. L\'enregistrer sur votre serveur</h3>' + bullets('<b>Chrome ou Edge</b> : ' + ui('Enregistrer dans le dossier de la pharmacie') + '. La première fois, choisissez le dossier des ordonnances : il est mémorisé sur ce poste.',
                '<b>Autre navigateur</b> : ' + ui('Télécharger le fichier') + ', puis rangez-le dans le dossier.')
        + tip('Nom du fichier', 'Le fichier est nommé automatiquement <b>Ordonnance_date_référence_initiales</b> ; ce nom devient le numéro interne de la vérification.'),
        win('p_scan', 'L\'ordonnance prête à être enregistrée'), wide=True)
      + split('<h3>3. Vérifier l\'ordonnance</h3>' + steps('Indiquez la <b>date de l\'ordonnance</b>.',
                'Indiquez sa <b>validité</b> : 1, 3, 6 ou 12 mois, ou une date précise.',
                'Contrôlez le numéro interne (rempli après un scan).',
                'Cochez <b>« La pharmacie détient l\'ordonnance originale… »</b> puis ' + ui('Enregistrer') + '.')
        + '<p>La location passe à <span class="tag t-o">Vérifiée</span>, visible sur tous les postes de la pharmacie et par le grossiste.</p>',
        win('p_presc', 'Vérification de l\'ordonnance'), rev=True, wide=True)
      + split('<h3>4. Revoir une ordonnance</h3><p>' + ui('Voir l\'ordonnance') + ' retrouve le fichier de cette location dans le dossier de votre serveur et l\'affiche. Le poste doit avoir accès à ce dossier.</p>'
        + '<h3>5. Renouveler</h3><p>14 jours avant l\'expiration (ou si la location dépasse la validité), la fiche affiche <span class="tag t-w">Nouvelle ordonnance à prévoir</span>, puis <span class="tag t-c">Ordonnance expirée</span>. Récupérez la nouvelle ordonnance, scannez-la et cliquez sur ' + ui('Enregistrer la nouvelle ordonnance') + '.</p>',
        crop('p_ordo_ok', 'Une ordonnance vérifiée'), wide=True)))
    ch.append(('Les e-mails de la pharmacie', 'Rappels d\'ordonnances et suivi des demandes',
      split('<p>Le portail vous écrit à l\'adresse de votre choix :</p>'
        + bullets('<b>Chaque matin, si besoin</b>, un récapitulatif des ordonnances à vérifier, à renouveler ou expirées ;',
                  '<b>Pour chaque demande</b>, un e-mail quand elle est planifiée, effectuée ou refusée.')
        + '<p>Le bénéficiaire n\'y figure que par ses initiales et sa commune ; le lien vers le portail demande la connexion.</p>'
        + '<h3>Changer l\'adresse</h3>' + steps('Menu ' + ui('Plus') + ' › ' + ui('E-mail des rappels') + '.', 'Une ou plusieurs adresses, séparées par une virgule.', ui('Enregistrer') + '. Laissez vide pour ne plus rien recevoir.'),
        win('p_mail', 'L\'adresse des e-mails'), wide=True)))
    ch.append(('La facturation', 'Vos montants de location, mois par mois',
      desk('p_fact', 'La facturation du mois')
      + bullets('Changez de mois avec les flèches. Le mois en cours est <b>prévisionnel</b> : les locations y sont comptées jusqu\'à la fin du mois.',
                '<b>Calcul</b> : jours de location dans le mois × tarif hebdomadaire ÷ 7. Le jour du retour n\'est pas facturé.',
                'Chaque ligne indique le bénéficiaire, le matériel, la période et la date de l\'ordonnance vérifiée.')
      + tip('Exporter', ui('Télécharger (CSV)') + ' crée un fichier pour Excel ; ' + ui('Copier pour un tableur') + ' copie les lignes à coller directement.')))
    ch.append(('Sur téléphone ou tablette', 'Le même portail, partout',
      '<p>Le portail s\'adapte à l\'écran : sur téléphone, le menu passe en bas et le bouton rond ' + ui('+') + ' ouvre les demandes. Ajoutez-le à l\'écran d\'accueil (iPhone : Partager › <i>Sur l\'écran d\'accueil</i> ; Android : menu ⋮ › <i>Installer l\'application</i>).</p>'
      + '<p>Chaque matériel porte une <b>étiquette NFC</b>. Approcher un téléphone de l\'étiquette ouvre directement sa fiche : pratique au comptoir quand un bénéficiaire rapporte du matériel. Sur ordinateur, utilisez la loupe et la référence (par exemple LIT-0101).</p>'))
    ch.append(('Questions fréquentes', 'Et comment nous joindre',
      faq(('Je ne vois pas une location de ma pharmacie.', 'Elle a peut-être été enregistrée au nom d\'une autre pharmacie : signalez-le au grossiste.'),
          ('Le matériel que je veux est « Sur demande ».', 'Envoyez quand même la demande : le grossiste vous répond avec une date ou propose un modèle équivalent.'),
          ('Je me suis trompé dans une demande.', 'Tant qu\'elle n\'est pas effectuée, ouvrez-la et cliquez sur « Annuler la demande », puis refaites-la.'),
          ('Je n\'arrive pas à enregistrer dans le dossier du serveur.', 'Utilisez Chrome ou Edge et vérifiez que le poste a accès au serveur. Sinon, « Télécharger le fichier » puis rangez-le à la main.'),
          ('« Voir l\'ordonnance » ne trouve rien.', 'Le nom du fichier doit contenir la référence du matériel (automatique avec « Scanner »). Vérifiez aussi le dossier : « Changer de dossier ».'),
          ('Je ne reçois pas les e-mails.', 'Vérifiez l\'adresse dans Plus › E-mail des rappels et le dossier des courriers indésirables.'))
      + f'<div class="contact"><b>Besoin d\'aide ?</b><br>{g["CONTACT"]}<br>Du lundi au vendredi, de 8 h à 16 h (heure de Tahiti).</div>'))
    intro = ('<div class="intro"><div class="c"><b>À qui s\'adresse ce guide ?</b>Aux pharmacies clientes qui demandent et suivent leurs locations de matériel médical, principalement depuis l\'ordinateur de l\'officine.</div>'
             '<div class="c"><b>Adresse du portail</b>https://manaprocess.cloud/materiel/<br>Identifiant et mot de passe fournis par le grossiste.</div></div>')
    quick = [('Se connecter', 'Adresse manaprocess.cloud/materiel, identifiant fourni par le grossiste, puis votre mot de passe personnel.'),
             ('Demander du matériel', 'Bouton « Nouvelle demande » › Location : produit, bénéficiaire, durée, date de livraison.'),
             ('Suivre et ajuster', 'Locations › Demandes : planifiée, effectuée… Prolongation, reprise ou problème depuis la fiche.'),
             ('Vérifier les ordonnances', 'Scan enregistré sur le serveur de la pharmacie, puis date et validité. Rappels avant expiration.')]
    return {'quick': quick, 'chips': ('Sur ordinateur',), 'file': 'guide-pharmacie.pdf', 'footer': 'MédiParc NFC · Guide du portail pharmacie', 'intro': intro, 'chapters': ch,
            'cover': ('Guide d\'utilisation', 'Portail<br>pharmacie', 'Demandez le matériel, suivez vos locations, vérifiez les ordonnances et contrôlez la facturation, depuis l\'ordinateur de l\'officine.',
                      'Pour les pharmacies clientes', [('p_home', 120)])}


# --------------------------------------------------------------------------------------------
def administrateur(g):
    h = _h(g); steps, bullets, tip, warn, key, split, faq, desk, win, crop = (h[k] for k in ('steps', 'bullets', 'tip', 'warn', 'key', 'split', 'faq', 'desk', 'win', 'crop'))
    ch = []
    ch.append(('Présentation et rôles', 'Le grossiste, ses techniciens et les pharmacies',
      '<p>MédiParc NFC organise toute la location de matériel médical : les pharmacies <b>demandent</b>, le grossiste <b>planifie et livre</b>, les techniciens <b>scannent</b> chaque matériel sur le terrain. Chaque équipement porte une étiquette NFC : on sait où il est, chez qui, depuis quand, dans quel état et ce qu\'il rapporte.</p>'
      + '<div class="roles"><div class="r"><span class="dv">Ordinateur</span><b>Administrateur</b>Tout le portail, plus les comptes, les pharmacies, les e-mails et l\'adresse des liens NFC.</div>'
      + '<div class="r"><span class="dv">Ordinateur et téléphone</span><b>Équipe du parc</b>Demandes, planning, parc, locations, entretien, rapports et facturation. Les techniciens utilisent le téléphone (guide du technicien).</div>'
      + '<div class="r"><span class="dv">Ordinateur</span><b>Pharmacie</b>Son portail : ses demandes, ses locations, ses ordonnances et sa facturation (guide du portail pharmacie).</div></div>'
      + desk('g_home', 'Le tableau de bord du grossiste')
      + key('Le circuit d\'une location', '<b>1.</b> La pharmacie envoie une demande › <b>2.</b> le grossiste la planifie › <b>3.</b> le technicien livre, scanne et photographie › <b>4.</b> la pharmacie vérifie l\'ordonnance › <b>5.</b> prolongation ou reprise à la demande › <b>6.</b> retour, désinfection, remise en stock.')))
    ch.append(('Connexion et sécurité', 'Première connexion et bonnes pratiques',
      split(steps('Ouvrez <b>https://manaprocess.cloud/materiel/</b>.', 'Identifiant <b>admin</b> et mot de passe provisoire remis à l\'installation.',
                  'Choisissez votre mot de passe : 10 caractères au moins, lettres et chiffres.')
        + warn('Un compte par personne', 'Créez un compte nominatif pour chaque membre de l\'équipe (chapitre 13) plutôt que de partager le compte admin : l\'historique indique qui a fait quoi. Après 8 essais erronés, la connexion est bloquée 15 minutes.')
        + tip('Sur ordinateur', 'Chrome ou Edge proposent d\'installer le portail comme un logiciel (icône dans la barre d\'adresse).'),
        win('g_pwd', 'Choix du mot de passe à la première connexion'), wide=True)))
    ch.append(('L\'écran principal', 'Menu, actions rapides et tableau de bord',
      split('<table class="t"><tr><th>Menu</th><th>Contenu</th></tr>'
        + '<tr><td><b>Actions rapides</b></td><td>Demandes, planning, scan, mise en location, retour, désinfection.</td></tr>'
        + '<tr><td><b>Accueil</b></td><td>Occupation, revenus, demandes des pharmacies, actions à traiter.</td></tr>'
        + '<tr><td><b>Parc</b></td><td>Tous les équipements : liste, plan, statistiques, maintenance.</td></tr>'
        + '<tr><td><b>Locations</b></td><td>Contrats, renouvellements, <b>demandes</b>, <b>planning</b>, terminés.</td></tr>'
        + '<tr><td><b>Entretien</b></td><td>Désinfections, maintenance, contrôles de sécurité.</td></tr>'
        + '<tr><td><b>Rapports</b></td><td>Rentabilité, utilisation, activité, exports, facturation.</td></tr>'
        + '<tr><td><b>Plus</b></td><td>Suivi des pharmacies, catalogue, paramètres NFC, comptes, guides.</td></tr></table>',
        win('g_quick', 'Les actions rapides'), wide=True)
      + h['annot']('g_home', [(16.3, 12.2), (16.3, 25.1), (16.3, 30.6), (16.3, 36.0), (16.3, 41.5), (16.3, 95.1), (95.2, 2.0), (21.6, 23.4), (21.6, 55.0), (86.6, 16.2)], 'Les repères du tableau de bord')
      + h['legend'](('Actions rapides', 'Demandes, planning, scan, location, retour.'), ('Parc', 'Tous les équipements.'), ('Locations', 'Contrats, demandes, planning.'),
                    ('Entretien', 'Désinfection, maintenance, contrôles.'), ('Rapports', 'Rentabilité, exports, facturation.'), ('Plus', 'Pharmacies, catalogue, comptes, guides.'),
                    ('Cloche', 'Actions à traiter, nouvelles demandes en tête.'), ('Occupation', 'Taux d\'occupation et revenus par semaine.'), ('Tuiles', 'Revenus, équipements, actions, maintenance.'), ('Paramètres', 'Étiquettes NFC et adresse des liens.'))
      + desk('g_home2', 'L\'accueil : demandes des pharmacies, planning, suivi, et la liste « À traiter »', small=True)
      + bullets('<b>Taux d\'occupation</b> et revenus par semaine ; cliquez sur un état (En location, Disponible…) pour la liste.',
                '<b>Demandes des pharmacies</b> : les nouvelles demandes, avec un accès direct au planning et au suivi des pharmacies.',
                '<b>À traiter</b> : nouvelles demandes, ordonnances expirées, contrôles en retard, retours du jour, désinfections en attente. La cloche en affiche le nombre.')))
    ch.append(('Traiter les demandes des pharmacies', 'Planifier, livrer, reprendre, prolonger ou refuser',
      desk('g_dem', 'Locations › Demandes : à traiter en haut, planifiées en dessous')
      + _tags([('Nouvelle', 't-w', 'Arrivée, à traiter. Elle s\'affiche aussi sur l\'accueil et dans la cloche.'),
               ('Urgent', 't-c', 'Nouvelle demande dont la date souhaitée est aujourd\'hui ou dépassée.'),
               ('Planifiée', 't-o', 'Une date de passage est fixée ; elle figure dans le planning des tournées.'),
               ('Effectuée / Refusée', 't-o', 'Clôturée ; visible dans l\'onglet Historique pendant 45 jours.')])
      + split('<h3>Ouvrir une demande</h3>' + bullets('Le détail : pharmacie, bénéficiaire et adresse, téléphone, matériel, durée, date souhaitée, précisions.',
                  '<b>Date de passage</b> et <b>message à la pharmacie</b> (facultatif, sauf pour refuser).',
                  ui('Planifier le passage') + ' : la demande passe en <span class="tag t-o">Planifiée</span>, la pharmacie est prévenue par e-mail.')
        + '<h3>Livrer une location</h3>' + steps('Dans la section <b>Livrer</b>, la liste montre les équipements <b>disponibles</b> de ce modèle (puis d\'autres modèles du même type).',
                  'Cliquez sur l\'équipement à livrer : la location démarre aujourd\'hui pour la durée demandée, au nom du bénéficiaire et de la pharmacie.',
                  'La demande passe en <span class="tag t-o">Effectuée</span>.')
        + tip('Sur le terrain', 'Le technicien peut faire la livraison directement depuis son téléphone, au moment où il installe le matériel.'),
        win('g_req_loc2', 'Une demande de location : planifier ou livrer'), wide=True)
      + split('<h3>Les autres demandes</h3><table class="t"><tr><th>Demande</th><th>Bouton</th><th>Effet</th></tr>'
        + '<tr><td>Reprise</td><td>' + ui('Reprise effectuée') + '</td><td>La location se termine, le matériel passe en désinfection.</td></tr>'
        + '<tr><td>Prolongation</td><td>' + ui('Accepter la prolongation') + '</td><td>La date de fin est repoussée de la durée demandée.</td></tr>'
        + '<tr><td>Problème</td><td>' + ui('Problème réglé sur place') + '<br>' + ui('Reprendre pour réparation') + '</td><td>Note dans l\'historique, ou passage en maintenance (la location s\'arrête).</td></tr>'
        + '<tr><td>Toutes</td><td>' + ui('Refuser la demande') + '</td><td>Le motif saisi est envoyé à la pharmacie.</td></tr></table>'
        + tip('Automatique', 'Un retour, une prolongation ou une panne enregistrés directement depuis la fiche clôturent aussi la demande correspondante.'),
        win('g_req_pb', 'Un problème signalé par une pharmacie'), wide=True)))
    ch.append(('Le planning des tournées', 'Livraisons, reprises et fins de location sur 14 jours',
      desk('g_plan', 'Locations › Planning')
      + bullets('Classé <b>par jour</b> (en retard, aujourd\'hui, demain…) puis <b>par commune</b> : on regroupe les passages d\'une même zone.',
                '<b>Livraisons</b> et <b>reprises</b> demandées par les pharmacies, planifiées ou encore <span class="tag t-w">À planifier</span>.',
                '<b>Fins de location</b> prévues, et <b>retours en retard</b> en rouge.',
                'Cliquez sur une ligne pour ouvrir la demande ou la fiche du matériel.')
      + tip('Envoyer la tournée au livreur', 'Le bouton ' + ui('Copier') + ' copie toute la tournée en texte (matériel, bénéficiaire, adresse, téléphone, pharmacie) : collez-la dans un SMS, WhatsApp ou un e-mail.')))
    ch.append(('Le suivi des pharmacies', 'Chaque pharmacie cliente en un coup d\'œil',
      split('<p>Menu ' + ui('Plus') + ' › ' + ui('Suivi des pharmacies') + ' (ou le bouton de l\'accueil) liste vos pharmacies avec leurs locations, loyers, retards, demandes et ordonnances à traiter.</p>'
        + '<p>Cliquez sur une pharmacie pour sa fiche :</p>'
        + bullets('Équipements en location, loyers par semaine, bénéficiaires ;', 'Retours en retard, fins sous 14 jours, ordonnances à traiter (en couleur s\'il y en a) ;',
                  'Ses demandes en cours ;', 'Boutons : ' + ui('Voir les contrats') + ', ' + ui('Facturation du mois') + ', ' + ui('Adresse e-mail des rappels') + '.')
        + tip('Dans les rapports', 'Rapports › Vue d\'ensemble › « Locations par pharmacie » ouvre aussi ces fiches.'),
        win('g_ph', 'La fiche de suivi d\'une pharmacie'), wide=True)))
    ch.append(('Le parc matériel', 'Inventaire, plan et statistiques',
      desk('g_parc', 'Parc › Liste : tuiles par état, recherche et filtres')
      + bullets('<b>Liste</b> : tous les équipements, filtrés par état, recherche par nom, référence ou bénéficiaire.',
                '<b>Plan</b> : où se trouve le matériel, commune par commune.',
                '<b>Statistiques</b> : répartition, occupation et rentabilité du parc.',
                '<b>Maintenance</b> : raccourci vers l\'entretien.')
      + '<div class="duo">' + desk('g_map', 'Parc › Plan', small=False) + desk('g_stats', 'Parc › Statistiques', small=False) + '</div>'))
    ch.append(('Mettre en location directement', 'Sans demande d\'une pharmacie',
      split(steps('Ouvrez la fiche d\'un équipement <b>Disponible</b> (Parc, filtre Disponible).', 'Cliquez sur ' + ui('Mettre en location') + '.',
                  'Choisissez la <b>durée</b>, la <b>pharmacie</b> et le <b>bénéficiaire</b> (ou ' + ui('Nouveau bénéficiaire') + ').',
                  'La location démarre ; la fiche affiche la durée écoulée et restante.')
        + tip('Préférez les demandes', 'Quand c\'est possible, laissez la pharmacie faire la demande : elle est tracée, et la pharmacie suit son avancement.'),
        win('g_assign', 'Mise en location'), wide=True)
      + desk('g_fiche_dispo', 'Fiche d\'un équipement disponible')))
    ch.append(('Les locations', 'Contrats, renouvellements et prolongations',
      desk('g_loc', 'Locations › Contrats en cours')
      + bullets('<b>Contrats en cours</b> : par bénéficiaire, avec la pharmacie, la durée écoulée, restante et le loyer.',
                '<b>À renouveler</b> : fins prévues sous 14 jours ; bouton ' + ui('+ 1 sem.') + ' pour prolonger aussitôt.',
                '<b>Demandes</b> et <b>Planning</b> : chapitres 4 et 5. <b>Terminés</b> : l\'historique.',
                'Menu à trois points d\'un bénéficiaire : le voir sur le plan, prolonger tout son matériel d\'une semaine.')
      + tip('Filtres', 'L\'entonnoir filtre par pharmacie ou par commune ; les flèches changent le tri.')))
    ch.append(('L\'entretien', 'Désinfection, maintenance et contrôles de sécurité',
      desk('g_ent', 'L\'écran Entretien')
      + '<table class="t"><tr><th>Section</th><th>Contenu</th><th>Action dans la fiche</th></tr>'
      + '<tr><td>À désinfecter</td><td>Matériel revenu de location.</td><td>' + ui('Valider la désinfection') + '</td></tr>'
      + '<tr><td>En maintenance</td><td>Matériel en panne, à l\'atelier.</td><td>' + ui('Clôturer la maintenance') + '</td></tr>'
      + '<tr><td>Prochains contrôles</td><td>Contrôles de sécurité à 7 ou 30 jours, retards en rouge.</td><td>' + ui('Contrôle effectué') + '</td></tr></table>'
      + tip('Démarche qualité', 'Chaque désinfection, réparation et contrôle est daté et signé dans l\'historique : c\'est la traçabilité attendue d\'une démarche de type ISO 9001.')))
    ch.append(('Rapports et rentabilité', 'Piloter le parc',
      desk('g_rap', 'Rapports › Vue d\'ensemble')
      + bullets('<b>Vue d\'ensemble</b> : loyers encaissés, investissement récupéré, occupation, locations par pharmacie.',
                '<b>Rentabilité</b> : pour chaque équipement, loyers encaissés par rapport au prix d\'achat.',
                '<b>Utilisation</b> : jours de location cumulés. <b>Activité</b> : les derniers événements.',
                '<b>Exports</b> : inventaire, contrats en cours, rentabilité, au format tableur.')))
    ch.append(('La facturation', 'Les montants de chaque mois, par pharmacie',
      desk('g_fact', 'Rapports › Facturation')
      + bullets('Choisissez le mois avec les flèches et une pharmacie (ou toutes).',
                '<b>Calcul</b> : jours de location dans le mois × tarif hebdomadaire ÷ 7 ; le jour du retour n\'est pas facturé. Le mois en cours est prévisionnel.',
                'Chaque ligne indique la date de l\'ordonnance vérifiée : une ligne « non vérifiée » est à régulariser avec la pharmacie.')
      + tip('Vers la comptabilité', ui('Télécharger (CSV)') + ' pour Excel ou votre logiciel de facturation ; ' + ui('Copier pour un tableur') + ' pour coller les lignes.')))
    ch.append(('Comptes, pharmacies et e-mails', 'Réservé à l\'administrateur',
      desk('g_accounts', 'Plus › Comptes et pharmacies')
      + split('<h3>Créer un compte</h3>' + steps(ui('Nouveau compte') + ' : nom affiché, identifiant, rôle (Pharmacie, Équipe du parc, Administrateur) et, pour une pharmacie, laquelle.',
                  'Un <b>mot de passe provisoire</b> s\'affiche une seule fois : ' + ui('Copier') + ' et transmettez-le avec l\'adresse et l\'identifiant.',
                  'À la première connexion, la personne choisit son propre mot de passe.')
        + bullets('Cliquez sur un compte pour <b>réinitialiser</b> son mot de passe ou le <b>désactiver</b> (départ d\'un salarié).',
                  ui('Nouvelle pharmacie') + ' : nom et commune d\'une nouvelle pharmacie cliente.'),
        win('g_newuser_pw', 'Le mot de passe provisoire à transmettre'), wide=True)
      + split('<h3>E-mails automatiques</h3>' + bullets('<b>Rappels d\'ordonnances</b> aux pharmacies, chaque matin à l\'heure choisie.',
                  '<b>Suivi des demandes</b> : la pharmacie est prévenue quand vous planifiez, effectuez ou refusez.',
                  '<b>Nouvelles demandes</b> : saisissez l\'adresse de l\'équipe pour être prévenu à chaque demande.',
                  'Voir les rappels en attente, envoyer un e-mail de test, envoyer maintenant.')
        + warn('Service d\'envoi', 'Les e-mails partent une fois le service d\'envoi branché sur le serveur (Resend, Brevo ou votre messagerie). Les réglages sont conservés en attendant.'),
        crop('g_mail', 'Les réglages des e-mails'), wide=True)))
    ch.append(('Étiquettes NFC et paramètres', 'Une étiquette, un lien, un équipement',
      split('<p>Chaque étiquette contient un lien du type <b>manaprocess.cloud/materiel/LIT-0101</b>. Le scanner ouvre la fiche de l\'équipement (sur téléphone) et enregistre le passage.</p>'
        + bullets('Plus › ' + ui('Paramètres') + ' : nombre d\'équipements étiquetés, liste des puces, adresse de base des liens.',
                  'Cliquez sur un équipement pour écrire son lien sur une puce, associer une puce déjà programmée, copier ou retirer le lien.',
                  'La pose et la programmation des étiquettes sur le terrain sont décrites dans le guide du technicien.'),
        win('g_tag', 'Le lien d\'une puce'), wide=True)
      + desk('g_settings', 'Plus › Paramètres : les puces NFC')))
    ch.append(('Données et confidentialité', 'Ce qui est enregistré, et ce qui ne l\'est jamais',
      '<table class="t"><tr><th>Donnée</th><th>Traitement</th></tr>'
      + '<tr><td>Bénéficiaire</td><td>Nom, adresse, commune, téléphone, <b>chiffrés</b> (AES-256). Anonymisé 3 ans après la dernière location.</td></tr>'
      + '<tr><td>Ordonnance</td><td><b>Jamais en ligne</b> : elle reste sur le serveur de la pharmacie. Seuls la date, la validité, le numéro interne et l\'auteur de la vérification sont enregistrés.</td></tr>'
      + '<tr><td>Données médicales</td><td>Aucune : ni pathologie, ni traitement, ni prescripteur.</td></tr>'
      + '<tr><td>Précisions des demandes</td><td>Chiffrées, 300 caractères au plus, effacées après 3 ans.</td></tr>'
      + '<tr><td>Positions des scans, photos</td><td>Effacées 3 ans après la fin de la location.</td></tr>'
      + '<tr><td>Comptabilité</td><td>Dates et montants de location conservés.</td></tr>'
      + '<tr><td>Sauvegardes</td><td>Copie quotidienne de la base, conservée 14 jours.</td></tr></table>'
      + warn('Clé de chiffrement', 'La clé de chiffrement du serveur (DATA_KEY) doit être conservée en lieu sûr : sans elle, les noms des bénéficiaires d\'une sauvegarde sont illisibles.')))
    ch.append(('Questions fréquentes', 'Et comment nous joindre',
      faq(('Une pharmacie demande un matériel qui n\'est pas disponible.', 'Planifiez la livraison à la date où un équipement revient, ou répondez en proposant un autre modèle ; vous pouvez aussi refuser avec un motif.'),
          ('Une pharmacie ne voit pas une location.', 'Vérifiez la pharmacie indiquée dans la fiche : elle ne voit que les locations à son nom.'),
          ('Un membre de l\'équipe a oublié son mot de passe.', 'Comptes et pharmacies › cliquez sur le compte › Réinitialiser le mot de passe.'),
          ('Une étiquette ouvre le mauvais équipement.', 'Ouvrez la bonne fiche et réécrivez le lien sur la puce : elle est réattribuée automatiquement.'),
          ('Les pharmacies ne reçoivent pas les e-mails.', 'Vérifiez qu\'une adresse est enregistrée pour la pharmacie et que le service d\'envoi est configuré (e-mail de test).'))
      + f'<div class="contact"><b>Assistance</b><br>{g["CONTACT"]}</div>'))
    intro = ('<div class="intro"><div class="c"><b>À qui s\'adresse ce guide ?</b>Au grossiste qui loue le matériel : administrateur et équipe du parc, sur l\'ordinateur du bureau.</div>'
             '<div class="c"><b>Les autres guides</b>Guide du portail pharmacie (pour vos clients) et guide du technicien (scan des étiquettes sur le téléphone), dans le menu Plus.</div></div>')
    quick = [('Créer les accès', 'Comptes et pharmacies : un compte par pharmacie et par membre de l\'équipe, mot de passe provisoire.'),
             ('Traiter les demandes', 'Accueil ou Locations › Demandes : planifier, livrer un équipement disponible, refuser.'),
             ('Organiser les tournées', 'Locations › Planning : passages par jour et par commune, à copier pour le livreur.'),
             ('Piloter le parc', 'Entretien, rapports de rentabilité, suivi des pharmacies et facturation mensuelle.')]
    return {'quick': quick, 'chips': ('Sur ordinateur', 'Équipe du parc'), 'file': 'guide-administrateur.pdf', 'footer': 'MédiParc NFC · Guide du grossiste', 'intro': intro, 'chapters': ch,
            'cover': ('Guide d\'utilisation', 'Portail<br>du grossiste', 'Traitez les demandes des pharmacies, planifiez les tournées, suivez le parc, l\'entretien, la rentabilité et la facturation.',
                      'Pour le grossiste', [('g_home', 120)])}


# --------------------------------------------------------------------------------------------
def technicien(g):
    h = _h(g); phone, crop, duo, steps, bullets, tip, warn, key, split, faq = (h[k] for k in ('phone', 'crop', 'duo', 'steps', 'bullets', 'tip', 'warn', 'key', 'split', 'faq'))
    flow = ('<div class="flow">' + ''.join(f'<div class="fs"><b>{a}</b><span>{b}</span></div>' for a, b in [
        ('Demande', 'pharmacie'), ('Livraison', 'scan + photo'), ('Chez le bénéficiaire', 'En location'), ('Reprise', 'scan + photo'), ('Désinfection', 'validation'), ('Dépôt', 'Disponible')]) + '</div>')
    ch = []
    ch.append(('Votre rôle sur le terrain', 'Le cycle de chaque équipement, et vos gestes à chaque étape',
      '<p>Vous êtes les yeux du parc. Chaque fois que vous touchez un matériel, vous le <b>scannez</b> avec votre téléphone : l\'application enregistre où il est, quand, et par qui. Avec une <b>photo horodatée</b>, son état est prouvé.</p>'
      + flow
      + '<table class="t"><tr><th>Étape</th><th>Vos gestes</th><th>Bouton</th></tr>'
      + '<tr><td>Préparer la tournée</td><td>Consulter le planning du jour</td><td>Locations › Planning</td></tr>'
      + '<tr><td>Livraison demandée</td><td>Scanner, livrer depuis la demande, photo « Livraison »</td><td>' + ui('Livrer') + '</td></tr>'
      + '<tr><td>Reprise demandée</td><td>Scanner, photo « Retour », reprise effectuée</td><td>' + ui('Reprise effectuée') + '</td></tr>'
      + '<tr><td>Désinfection</td><td>Nettoyer, puis valider</td><td>' + ui('Valider la désinfection') + '</td></tr>'
      + '<tr><td>Panne</td><td>Photo « Panne », signaler</td><td>' + ui('Signaler une panne') + '</td></tr>'
      + '<tr><td>Contrôle de sécurité</td><td>Contrôler, puis enregistrer</td><td>' + ui('Contrôle effectué') + '</td></tr>'
      + '<tr><td>Nouvelle étiquette</td><td>Coller, programmer, tester</td><td>' + ui('Écrire le lien sur une puce') + '</td></tr></table>'
      + key('La règle d\'or', 'Un matériel touché = un matériel scanné. C\'est ce qui rend la localisation et l\'historique fiables.')))
    ch.append(('Préparer son téléphone', 'À faire une seule fois',
      split(steps('<b>iPhone</b> : installez l\'application fournie par l\'administrateur. Elle seule permet de lire et d\'écrire les étiquettes sur iPhone.',
                  '<b>Android</b> : ouvrez <b>https://manaprocess.cloud/materiel/</b> dans <b>Chrome</b>, puis menu ⋮ › ' + ui('Installer l\'application') + '. Activez le <b>NFC</b> dans les réglages.',
                  'Connectez-vous avec <b>votre</b> identifiant (rôle « Équipe du parc ») et choisissez votre mot de passe.',
                  'Au premier scan et à la première photo, <b>autorisez la localisation et l\'appareil photo</b>.')
        + warn('Compte personnel', 'Ne prêtez pas votre compte : l\'historique indique qui a scanné, livré ou désinfecté. Verrouillez le téléphone par un code.')
        + tip('Réseau', 'Les actions sont enregistrées en ligne. Sans réseau, attendez une connexion avant de valider, puis vérifiez l\'historique.'),
        phone('t_home', 'L\'accueil sur le téléphone'))))
    ch.append(('La tournée du jour', 'Savoir où aller, dans quel ordre',
      split(steps('Touchez ' + ui('Locations') + ' puis l\'onglet <b>Planning</b>.',
                  'Les passages sont classés <b>par jour</b>, puis <b>par commune</b> : livraisons, reprises, fins de location, retards.',
                  'Touchez une ligne pour ouvrir la demande : adresse, téléphone du bénéficiaire (touchez pour appeler), précisions de la pharmacie.')
        + tip('Tournée par message', 'Le gestionnaire peut aussi vous envoyer la tournée par SMS ou WhatsApp : il la copie depuis le planning.'),
        phone('t_plan', 'Le planning des tournées'))))
    ch.append(('Scanner une étiquette', 'Ouvrir la fiche d\'un équipement en 2 secondes',
      steps('Touchez le bouton rond ' + ui('+') + ' en bas de l\'écran.', 'Touchez ' + ui('Scanner une puce NFC') + '.',
            'Approchez l\'étiquette : <b>le haut de l\'iPhone</b>, ou <b>le dos d\'un Android</b> (au milieu), à 1 ou 2 cm, sans bouger.',
            'La fiche s\'ouvre. Le scan est enregistré avec la date, votre nom et la position.')
      + duo('t_quick', 'Actions rapides', 't_scan', 'En attente de l\'étiquette')
      + split('<h3>Ce que vous vérifiez dans la fiche</h3>'
        + bullets('<b>L\'état</b> en haut à droite : En location, Disponible, Désinfection, Maintenance.',
                  '<b>L\'emplacement</b> et le <b>bénéficiaire</b> (touchez le téléphone pour appeler).',
                  '<b>Le prochain contrôle de sécurité</b>, en rouge s\'il est en retard.',
                  '<b>Le dernier scan</b> : date, auteur, et lien <b>Position</b> vers la carte.')
        + tip('Sans l\'application, sur iPhone', 'Approcher l\'étiquette d\'un iPhone déverrouillé affiche une notification qui ouvre la fiche dans Safari ; le scan est aussi enregistré.'),
        crop('t_kv', 'Les informations de la fiche'))))
    ch.append(('Livrer une demande de location', 'Installer le matériel et démarrer la location',
      split(steps('Ouvrez la demande (Planning ou Locations › Demandes) et vérifiez le bénéficiaire, l\'adresse et les précisions.',
                  'Au dépôt ou chez le bénéficiaire, dans la section <b>Livrer</b>, touchez l\'équipement que vous installez : la location démarre au nom du bénéficiaire et de la pharmacie.',
                  'Installez le matériel, puis <b>scannez</b> l\'étiquette pour enregistrer la position.',
                  'Touchez ' + ui('Prendre une photo horodatée') + ', choisissez <b>Livraison</b>, photographiez le matériel installé.')
        + warn('Photographier le matériel seulement', 'Jamais le bénéficiaire, ses proches, ses papiers ou ses médicaments.')
        + tip('Sans demande ?', 'Pour une livraison décidée par le gestionnaire, ouvrez la fiche d\'un équipement Disponible et touchez ' + ui('Mettre en location') + '.'),
        phone('t_req', 'Une demande : planifier ou livrer'))
      + crop('t_photos', 'La photo de livraison, avec date, heure, référence, auteur et position incrustées')))
    ch.append(('Reprendre le matériel', 'Reprise demandée ou fin de location',
      split(steps('Chez le bénéficiaire, <b>scannez</b> l\'étiquette.',
                  'Photo horodatée <b>Retour</b> : l\'état du matériel au moment de la reprise est prouvé.',
                  'Ouvrez la demande de reprise et touchez ' + ui('Reprise effectuée') + ' (ou, sans demande, ' + ui('Enregistrer le retour') + ' dans la fiche). La location se termine, le matériel passe en <b>Désinfection</b>.',
                  'Au dépôt, déposez-le en zone de lavage.')
        + tip('Comparer', 'Dans l\'historique, la photo de livraison et celle du retour se suivent : une casse se voit immédiatement.')
        + warn('Matériel endommagé', 'Photo de retour, retour enregistré, puis signalez la panne avec une photo <b>Panne</b> du dommage.'),
        phone('t_req_rep', 'Une demande de reprise'))))
    ch.append(('Désinfection et remise en stock', 'Rendre le matériel à nouveau disponible',
      steps('Ouvrez ' + ui('Entretien') + ' : la section <b>À désinfecter</b> liste le matériel revenu.',
            'Désinfectez selon la procédure de l\'entreprise.',
            '<b>Scannez</b> l\'étiquette (ou touchez la ligne) puis ' + ui('Valider la désinfection') + '.',
            'Le matériel passe en <b>Disponible</b> : il peut être livré à la prochaine demande.')
      + duo('t_ent', 'Entretien › À désinfecter', 't_desinf', 'Valider la désinfection')))
    ch.append(('Panne et maintenance', 'Signaler, réparer, remettre en service',
      split('<h3>Signaler une panne</h3>' + steps('Scannez l\'équipement.', 'Photo horodatée <b>Panne</b> sur le défaut.', 'Touchez ' + ui('Signaler une panne') + ' : l\'équipement passe en <b>Maintenance</b> ; une location en cours s\'arrête.')
        + '<h3>Problème signalé par une pharmacie</h3><p>Ouvrez la demande « Problème » : ' + ui('Problème réglé sur place') + ' si vous avez pu régler, ou ' + ui('Reprendre pour réparation') + '.</p>'
        + '<h3>Après réparation</h3>' + steps('Scannez l\'équipement.', 'Touchez ' + ui('Clôturer la maintenance') + ' : il redevient <b>Disponible</b>.')
        + warn('Sécurité', 'Un matériel défectueux ne doit jamais rester chez un bénéficiaire. En cas de doute, retirez-le.'),
        phone('t_maint', 'Un équipement en maintenance'))))
    ch.append(('Contrôles de sécurité', 'Tenir à jour les vérifications périodiques',
      split(steps(ui('Entretien') + ' › <b>Prochains contrôles</b> (7 ou 30 jours). Les retards apparaissent aussi sur l\'accueil.',
                  'Effectuez le contrôle.',
                  '<b>Conforme</b> : dans la fiche, ligne « Prochain contrôle », touchez ' + ui('Contrôle effectué') + ' : prochain contrôle dans un an.',
                  '<b>Non conforme</b> : ' + ui('Signaler une panne') + '.'),
        crop('t_check', 'Le bouton « Contrôle effectué »'))))
    ch.append(('Poser et programmer une étiquette', 'Pour chaque nouvel équipement, ou pour remplacer une étiquette',
      '<table class="t"><tr><th>Matériel</th><th>Où coller l\'étiquette</th></tr>'
      + '<tr><td>Lit médicalisé</td><td>Châssis métallique, côté tête de lit, partie plane, à l\'abri des articulations.</td></tr>'
      + '<tr><td>Lève-personne, verticalisateur</td><td>Sur le mât, à hauteur de main, côté opposé aux sangles.</td></tr>'
      + '<tr><td>Fauteuil, déambulateur, rollator</td><td>Cadre sous l\'assise ou traverse, à l\'abri des frottements.</td></tr>'
      + '<tr><td>Aérosol, concentrateur, tire-lait, TENS</td><td>Face arrière ou dessous du boîtier, loin des aérations.</td></tr></table>'
      + split(bullets('Étiquettes <b>anti-métal</b> sur toute surface métallique.', 'Surface nettoyée et sèche, appuyez 30 secondes.', 'Toujours au même endroit pour un même type de matériel.')
        + '<h3>Programmer</h3>' + steps('Ouvrez la fiche de l\'équipement.', 'Touchez ' + ui('Écrire le lien sur une puce') + '.', 'Approchez le téléphone jusqu\'au message de réussite.', '<b>Testez</b> : ' + ui('+') + ' › ' + ui('Scanner une puce NFC') + ' doit ouvrir la bonne fiche.'),
        phone('t_write', 'Écriture de l\'étiquette'))))
    memo = ('<table class="t memo"><tr><th>Situation</th><th>Gestes, dans l\'ordre</th></tr>'
      + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in [
        ('Tournée du jour', 'Locations › Planning'),
        ('Ouvrir une fiche', '+ › Scanner une puce NFC › approcher l\'étiquette'),
        ('Livraison demandée', 'Demande › Livrer (choisir l\'équipement) › scanner › Photo « Livraison »'),
        ('Reprise demandée', 'Scanner › Photo « Retour » › Demande › Reprise effectuée'),
        ('Désinfection faite', 'Scanner › Valider la désinfection'),
        ('Panne', 'Scanner › Photo « Panne » › Signaler une panne'),
        ('Réparation terminée', 'Scanner › Clôturer la maintenance'),
        ('Contrôle conforme', 'Scanner › Contrôle effectué'),
        ('Nouvelle étiquette', 'Coller › fiche › Écrire le lien sur une puce › tester')]) + '</table>')
    ch.append(('Aide-mémoire', 'À garder dans le véhicule', memo
      + '<div class="contact"><b>Un doute ? Un problème ?</b><br>Appelez le gestionnaire du parc.<br>Assistance de l\'application : ' + g['CONTACT'] + '</div>'))
    ch.append(('Problèmes fréquents', 'Les solutions rapides',
      faq(('L\'étiquette ne se lit pas.', 'NFC activé (Android), téléphone déverrouillé, coque épaisse retirée. Approchez lentement, au bon endroit (haut de l\'iPhone, milieu du dos d\'un Android).'),
          ('« Lecture NFC indisponible » sur iPhone.', 'Vous êtes dans Safari : utilisez l\'application iPhone, ou approchez simplement l\'étiquette pour ouvrir la fiche.'),
          ('Pas d\'équipement à livrer dans la demande.', 'Aucun équipement de ce modèle n\'est disponible : prévenez le gestionnaire, qui choisira un autre modèle ou une autre date.'),
          ('L\'étiquette ouvre le mauvais équipement.', 'Ouvrez la bonne fiche et touchez « Écrire le lien sur une puce » : l\'étiquette est réattribuée.'),
          ('La position n\'est pas enregistrée.', 'Autorisez la localisation pour l\'application (ou le navigateur) dans les réglages du téléphone.'),
          ('Le bouton attendu n\'apparaît pas.', 'Les boutons dépendent de l\'état du matériel : vérifiez l\'état en haut de la fiche.'))))
    intro = ('<div class="intro"><div class="c"><b>À qui s\'adresse ce guide ?</b>Aux techniciens et livreurs qui livrent, reprennent, désinfectent, contrôlent le matériel et posent les étiquettes NFC.</div>'
             '<div class="c"><b>Ce qu\'il vous faut</b>Un téléphone avec NFC : iPhone avec l\'application, ou Android avec Chrome. Votre identifiant personnel.</div></div>')
    quick = [('Préparer le téléphone', 'Application iPhone ou Chrome sur Android, NFC activé, votre identifiant personnel.'),
             ('Consulter la tournée', 'Locations › Planning : livraisons, reprises et fins de location du jour.'),
             ('Scanner chaque matériel', 'Bouton + › Scanner une puce NFC : la fiche s\'ouvre, le passage et la position sont enregistrés.'),
             ('Prouver par la photo', 'Photo horodatée à chaque livraison, reprise ou panne, puis l\'action dans la fiche.')]
    return {'quick': quick, 'chips': ('Sur téléphone',), 'file': 'guide-technicien.pdf', 'footer': 'MédiParc NFC · Guide du technicien', 'intro': intro, 'chapters': ch,
            'cover': ('Guide d\'utilisation', 'Technicien<br>et livreur', 'La tournée du jour, le scan des étiquettes NFC, les livraisons, reprises, désinfections et contrôles, avec des photos horodatées.',
                      'Pour les techniciens et livreurs', [('t_plan', 40), ('t_fiche', 40)])}
