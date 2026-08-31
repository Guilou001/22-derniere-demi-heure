#set document(title: "La première demi-heure ne prédit plus la dernière, et ce n'est pas la nuance qu'on attendait", author: "Guillaume Vaudescal")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(90))
    #grid(columns: (1fr, auto), align: (left, right),
      [derniere-demi-heure], [#counter(page).display("1 / 1", both: true)])
  ],
)
#set text(font: ("Helvetica", "Arial", "DejaVu Sans"), size: 10pt, lang: "fr")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)
#set heading(numbering: none)
#show heading.where(level: 2): it => block(above: 1.6em, below: 0.8em, text(size: 13pt, it))
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, it))
#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, text(size: 8.5pt, it))
#show raw.where(block: false): it => text(size: 9pt, fill: rgb("#1a3f66"), it)
#show quote.where(block: true): it => block(
  inset: (left: 10pt), stroke: (left: 1.5pt + luma(180)),
  text(style: "italic", fill: luma(45), it.body))
// la table NE DOIT PAS être enfermée dans un par() : Typst 0.15 la supprime alors
// entièrement, sans erreur. Le réglage se pose donc dans la portée du bloc.
#show table: it => block(above: 1.1em, below: 1.1em,
  [#set par(justify: false); #text(size: 8.8pt, it)])
#show figure: it => block(above: 1.4em, below: 1.4em, it)
#show figure.caption: it => text(size: 8.5pt, fill: luma(70), it)
#show link: it => text(fill: rgb("#0072B2"), it)

#align(center)[
  #block(width: 100%)[
    #text(size: 18pt, weight: "bold")[La première demi-heure ne prédit plus la dernière, et ce n'est pas la nuance qu'on attendait]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-08-31 · #link("https://github.com/Guilou001/22-derniere-demi-heure")[Guilou001/22-derniere-demi-heure]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Un article du Journal of Financial Economics montre qu'entre 1993 et 2013, la première demi-heure, mesurée depuis la clôture de la veille, prédisait la dernière. Rejoué sur 2016-2026 et sur huit fonds indiciels, *le signe s'inverse sur six d'entre eux*. Le renversement penche du côté que l'article disait le plus favorable, les jours volatils et les jours de fort volume, sans qu'aucun écart entre tiers soit établi.

*Résultat.* Sur huit fonds indiciels de 2016 à 2026, et jusqu'à 2 649 séances chacun, la pente de la première demi-heure sur la dernière est *négative pour six fonds sur huit*, de médiane −0,018. Aucun fonds d'actions ne montre de pente positive. Ce qui subsiste est un effet bien plus modeste, l'avant-dernière demi-heure prédisant la dernière, *positif sur les huit*. Il meurt à *0,06 à 0,51 point de base* de coût par passage selon le fonds.

_Summary in English. Gao, Han, Li and Zhou (JFE 2018) document market intraday momentum: the first half-hour return, measured from the previous close, predicts the last half-hour return on SPY over 1993-2013. Replayed on 2016-2026 across eight liquid ETFs, with up to 2,649 sessions each, the slope is negative for six of eight, median −0.018, and no equity fund shows a positive slope. The reversal leans the way the paper said its effect was strongest, on high-volatility and high-volume days, on seven of the eight fund-criterion pairs, though only one of the eight high-minus-low differences exceeds two standard errors. Decomposing the signal shows the overnight gap carries all of it, not the first half-hour of trading. A weaker relation does survive, the twelfth half-hour predicting the thirteenth, positive on all eight funds, but it breaks even at 0.06 to 0.51 basis points per trade on the four US index funds, and is already losing money at zero cost on EEM. Finally, of the 78 half-hour pairs testable on SPY, four exceed a two standard error threshold where chance alone would give 3.5._

== 1. L'affirmation, et le détail qui décide de tout

*Ce que l'article affirme.* Son résumé, relevé le 30 août 2026 sur la notice EconPapers :

#quote(block: true)[the first half-hour return on the market as measured from the previous day's market close predicts the last half-hour return. This predictability, which is both statistically and economically significant, is stronger on more volatile days, on higher volume days, on recession days, and on major macroeconomic news release days. Intraday momentum also exists for ten other most actively traded domestic and international ETFs.]

*En mots simples.* La séance américaine dure de 9 h 30 à 16 h, soit treize demi-heures. L'affirmation est que si le marché monte le matin, il tend à monter encore juste avant la clôture. Assez pour qu'on puisse en vivre, dit l'article.

*Un détail qui décide de tout.* Sa première demi-heure ne commence pas à l'ouverture : elle se mesure *depuis la clôture de la veille*, donc elle contient la nuit. C'est écrit dans le résumé, et c'est la première chose qu'une réplication rate.

*La question du dépôt.* Une anomalie publiée se juge sur ce qu'elle fait après sa publication, et non sur la reproduction de ses propres chiffres. L'article s'arrête en 2013 ; ce dépôt commence en 2016.

== 2. D'où vient le projet, et ce qu'il apporte

Trois apports.

- *L'affirmation éprouvée sur huit fonds*, et non sur un seul, ce qui met à l'épreuve la

généralisation que l'article annonce lui-même.

- *La décomposition du signal* entre la nuit et la première demi-heure de bourse, que l'article ne

fait pas et qui change la lecture de l'effet.

- *La matrice complète des 78 paires de demi-heures*, qui situe la case retenue par l'article

parmi toutes celles qu'on aurait pu retenir.

=== Ce qui n'a pas été obtenu, et c'est un résultat

Les tables chiffrées de l'article n'ont pas pu être lues. Trois chemins essayés le 30 août 2026. L'éditeur oppose une vérification anti-robot, et le dépôt SSRN refuse le téléchargement direct. L'adresse que le registre du portefeuille tenait pour un PDF universitaire rend en réalité une page HTML de 138 370 octets. Les coefficients et statistiques publiés ne sont donc *pas* reproduits ici, et ce dépôt ne le prétend pas. Ce qui est testé, ce sont les *affirmations* du résumé, sur une fenêtre que l'article ne couvre pas.

== 3. Les données, et les trois choix qu'elles imposent

Barres d'une minute du *flux consolidé*, de janvier 2016 au 28 août 2026, téléchargées chez Alpaca par le client partagé du portefeuille.

#table(
  columns: 3,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Fonds*],
    [*Ce qu'il suit*],
    [*Séances retenues*],
    [SPY, QQQ, IWM],
    [S&P 500, Nasdaq 100, Russell 2000],
    [2 649],
    [DIA],
    [Dow Jones],
    [1 864],
    [EEM, EFA],
    [marchés émergents, marchés développés hors Amérique],
    [2 566 et 2 571],
    [GLD, TLT],
    [or, obligations du Trésor à long terme],
    [2 560 et 2 444],
)

Le flux consolidé et non celui d'IEX. Le dépôt voisin #link("https://github.com/Guilou001/24-vwap-iex-vs-consolide")[24-vwap-iex-vs-consolide] mesure sur QQQ, du 3 août 2020 au 28 août 2026, qu'IEX porte *1,37 %* du volume consolidé et publie une barre dans *91,9 %* des minutes de séance. Le problème n'est donc pas qu'IEX se taise, c'est que son prix diffère : sa moyenne pondérée s'écarte de *9,61 cents* en médiane. Une mesure antérieure de ce portefeuille annonçait 57 % de minutes muettes ; ce compte porte sur la journée entière, extensions d'avant et d'après-bourse comprises, et non sur les 390 minutes de séance où ce dépôt travaille.

Des prix *bruts* et non ajustés. Les deux fournisseurs de données n'entendent pas la même chose par « ajusté », et les mêler poserait une marche de onze points de base à chaque détachement. Le détachement n'a pas d'effet de r2 à r13, qui vivent à l'intérieur d'une séance. Il en a un sur r1, qui traverse la nuit, et *ces séances ne sont pas retirées*. Mesuré sur le S&P 500, sur les 41 troisièmes vendredis de trimestre de la fenêtre : r1 y vaut *−55,16 points de base* en moyenne contre +4,70 ailleurs, et il y est négatif 92,7 % du temps contre 43,6 %. Retirer ces 41 séances déplace la pente de tête de −0,0557 (t = −2,10) à −0,0569 (t = −2,18), donc le verdict tient. Déclaré, non corrigé.

Le Dow Jones perd *30,4 %* de ses séances au filtre de complétude : sur les 2 679 séances présentes dans ses barres, 814 comptent moins de 390 barres d'une minute. Les sept autres fonds en perdent de 1,1 % pour le S&P 500 à 8,7 % pour les obligations du Trésor. Ce n'est pas un choix, c'est une limite de ses données, et elle est déclarée.

== 4. Le découpage fait tout le travail, la régression ne fait que conclure

+ *Découper chaque séance en treize demi-heures*, chaque barre étant rangée dans la demi-heure où elle commence, la barre de 16 h qui porte l'enchère de clôture rejoignant la treizième.
+ *Contrôler le découpage* par trois mesures : l'identité de composition, le nombre de barres de chaque demi-heure, et la coïncidence des prix de bord avec ceux d'une copie des barres remise en désordre. Seules les deux dernières peuvent échouer.
+ *Retirer les séances écourtées*, celles de veille de congé qui ferment à 13 h, où la dernière demi-heure n'existe pas.
+ *Régresser* la treizième demi-heure sur la première, avec des erreurs types de Newey et West. Les jours agités arrivent en grappes, et l'erreur type ordinaire fabriquerait de la significativité là où il n'y a que de la persistance.
+ *Facturer la stratégie*, deux passages de marché par jour, et chercher le coût qui l'annule.

== 5. Ce que les données répondent

=== 5.1 Le contrôle du découpage qui compte n'est pas celui qu'on croit

Trois mesures tournent à chaque exécution, sur les huit fonds. Le découpage porte sur 19 960 séances, dont 19 952 restent utilisables une fois la clôture de la veille exigée, la première séance de chaque fonds n'en ayant pas.

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Contrôle*],
    [*Ce qu'il rend*],
    [Écart à l'identité de composition, le pire],
    [1,1 × 10⁻¹⁵],
    [Écart à l'identité de composition, la médiane],
    [2,2 × 10⁻¹⁶],
    [Demi-heures découpées],
    [259 480],
    [Demi-heures à qui il manque une minute],
    [1 231],
    [Prix de bord déplacés par un mélange des barres],
    [0],
)

Comment lire ce tableau, en trois constats. Le premier est que *l'identité de composition ne peut pas échouer*. Le produit des treize rendements télescope en le rapport du dernier prix à la clôture de la veille, et le rendement du jour est bâti de ces deux mêmes prix. Elle tient donc à 10⁻¹⁵ sur des barres entièrement mélangées, elle mesure l'arrondi de la machine, et un test du dépôt fige cette limite pour qu'on cesse de la lire comme une garantie. Le deuxième est que les deux autres mesures, elles, peuvent échouer. 1 231 demi-heures sur 259 480, soit 0,47 %, ont perdu une minute, toutes sur les cinq fonds les moins échangés. Le prix de fin y est celui d'une minute antérieure. Le troisième est qu'aucun prix de bord ne bouge quand on mélange les lignes d'entrée, donc le découpage lit bien l'heure que porte chaque barre et non son rang d'arrivée. C'est le défaut qui a déjà frappé ce portefeuille ailleurs, un horodatage mal lu appariant les prix aux mauvaises minutes sans changer ni le nombre de lignes ni les colonnes.

=== 5.2 Six fonds sur huit ont la pente à l'envers

La statistique de Student, la pente divisée par son erreur type, dit de combien d'erreurs types la pente s'écarte de zéro. Le hasard seul explique mal un écart au-delà de deux.

#table(
  columns: 6,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Fonds*],
    [*Ce qu'il suit*],
    [*Pente*],
    [*Erreur type*],
    [*Student*],
    [*Stratégie, par an*],
    [*SPY*],
    [S&P 500],
    [*−0,056*],
    [0,026],
    [*−2,10*],
    [−3,5 %],
    [DIA],
    [Dow Jones],
    [−0,040],
    [0,029],
    [−1,39],
    [−3,6 %],
    [QQQ],
    [Nasdaq 100],
    [−0,035],
    [0,018],
    [−1,88],
    [−2,9 %],
    [IWM],
    [Russell 2000],
    [−0,029],
    [0,016],
    [−1,86],
    [−3,9 %],
    [EEM],
    [marchés émergents],
    [−0,008],
    [0,008],
    [−1,00],
    [−1,8 %],
    [EFA],
    [marchés développés hors Amérique],
    [−0,008],
    [0,011],
    [−0,70],
    [−0,5 %],
    [TLT],
    [obligations du Trésor],
    [+0,001],
    [0,009],
    [+0,15],
    [+0,7 %],
    [*GLD*],
    [or],
    [*+0,016*],
    [0,007],
    [*+2,35*],
    [+1,4 %],
)

Comment lire ce tableau, en trois constats. Le premier est que *aucun des six fonds d'actions n'a de pente positive* : l'affirmation de l'article ne survit pas, et pas seulement en perdant sa significativité. Le deuxième est que le seul coefficient significativement positif de ces huit-ci est celui de l'or, qui n'est pas un indice d'actions. Un dépassement du seuil sur huit tests reste dans l'ordre de grandeur du hasard, et il ne faut pas le lire autrement. Le troisième est que la stratégie qui suivrait le signal perd de l'argent *avant même* de payer le moindre frais sur six fonds sur huit. Une réserve pour finir : les huit fonds bougent ensemble, donc leurs huit pentes ne sont pas huit épreuves indépendantes de l'affirmation.

#figure(image("../results/figures/huit_fonds.png", width: 100%), caption: [La pente de chaque fonds, pour les deux signaux])

Comment lire cette figure : une barre par fonds, la pente de la régression, avec deux erreurs types de part et d'autre. À gauche le signal de l'article, à droite l'avant-dernière demi-heure. Les couleurs distinguent le signe, non la significativité.

=== 5.3 Le renversement tient à chaque sous-période

#table(
  columns: 5,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Fonds*],
    [*2016-2019*],
    [*2020-2021*],
    [*2022-2026*],
    [*Sans 2020*],
    [SPY],
    [−0,051],
    [−0,094],
    [−0,017],
    [−0,033 (t = −2,55)],
    [QQQ],
    [−0,035],
    [−0,075],
    [−0,011],
    [−0,021 (t = −2,19)],
    [IWM],
    [−0,006],
    [−0,052],
    [−0,012],
    [−0,014],
    [DIA],
    [−0,036],
    [−0,066],
    [−0,005],
    [−0,020],
)

Comment lire ce tableau, en trois constats. Le premier est que *les seize cellules sont négatives*, sans exception, ce qu'un simple effet de bruit ne produirait pas. Le deuxième est que retirer 2020, l'année où l'on soupçonnerait un régime à part, ne rétablit rien. La pente reste négative, et sa statistique de Student *augmente* en valeur absolue sur trois des quatre fonds, parce que retirer les séances les plus agitées réduit surtout la variance. Le Russell 2000 fait exception, la sienne passant de −1,86 à −1,78. Le troisième est que l'effet s'atténue depuis 2022, en valeur absolue, sans que ce dépôt teste ce qui explique cette atténuation. Le tableau laisse une chose de côté : les quatre fonds partagent leurs séances, donc seize cellules négatives ne valent pas seize épreuves.

#figure(image("../results/figures/periodes.png", width: 100%), caption: [La pente par période et par fonds])

Comment lire cette figure : quatre groupes de quatre barres, un groupe par colonne du tableau et une barre par fonds. Les seize passent sous zéro. La quatrième colonne recouvre les trois premières au lieu de s'y ajouter, et aucune barre ne porte son erreur type.

=== 5.4 Le renversement penche du côté annoncé, mais aucun écart entre tiers n'est établi

L'article annonce que sa prédictibilité est « plus forte les jours plus volatils, les jours de plus fort volume ». Chaque fonds est donc découpé en tiers d'effectif égal, sur les deux critères, et la dernière colonne éprouve l'écart lui-même :

#table(
  columns: 7,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Fonds*],
    [*Critère*],
    [*bas*],
    [*moyen*],
    [*haut*],
    [*haut moins bas*],
    [*Student de l'écart*],
    [SPY],
    [volatilité],
    [+0,014],
    [−0,015],
    [−0,059],
    [−0,073],
    [−0,85],
    [SPY],
    [volume],
    [+0,006],
    [−0,057],
    [−0,061],
    [−0,067],
    [−1,62],
    [QQQ],
    [volatilité],
    [+0,062],
    [−0,021],
    [−0,037],
    [−0,099],
    [−1,39],
    [QQQ],
    [volume],
    [−0,020],
    [−0,027],
    [−0,039],
    [−0,019],
    [−0,65],
    [IWM],
    [volatilité],
    [−0,043],
    [−0,013],
    [−0,030],
    [*+0,013*],
    [+0,24],
    [IWM],
    [volume],
    [−0,029],
    [−0,024],
    [−0,030],
    [−0,001],
    [−0,05],
    [DIA],
    [volatilité],
    [−0,011],
    [−0,026],
    [−0,042],
    [−0,031],
    [−0,50],
    [DIA],
    [volume],
    [+0,023],
    [−0,010],
    [−0,065],
    [*−0,088*],
    [*−2,06*],
)

Les tiers étant disjoints, l'erreur type de l'écart est la racine de la somme des carrés des deux erreurs types. Sur les 24 pentes de tiers, deux seulement dépassent deux erreurs types, toutes deux sur le S&P 500 : le tiers moyen par volume (t = −3,41) et le tiers haut par volatilité (t = −2,03).

Comment lire ce tableau, en trois constats. Le premier est que le conditionnement annoncé se retrouve *dans l'autre sens* sur sept des huit couples. L'écart entre le tiers haut et le tiers bas est négatif partout sauf sur le Russell 2000 par volatilité, où il est positif et où la progression n'est même pas monotone. Le deuxième est qu'une pente positive n'apparaît que dans le tiers calme, sur quatre couples sur huit, et jamais au-delà de 1,81 erreur type de zéro. Le troisième est ce que le tableau n'établit pas. Un seul des huit écarts dépasse deux erreurs types, là où le hasard seul en donnerait 0,4, au taux par essai qui donne les 3,5 de la section 5.7. Le dépôt mesure donc un penchant et non une différence prouvée, et la discipline appliquée à l'or en 5.2 s'applique ici aussi.

=== 5.5 Ce qui prédit n'est pas la demi-heure de bourse, c'est la nuit

La première demi-heure de l'article contient deux choses : l'écart entre la clôture de la veille et l'ouverture, puis la première demi-heure de séance. Les séparer :

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Fonds*],
    [*Depuis la veille*],
    [*La nuit seule*],
    [*La séance seule*],
    [SPY],
    [−0,056 (t = −2,10)],
    [*−0,056 (t = −2,17)*],
    [−0,070 (t = −1,19)],
    [QQQ],
    [−0,035 (t = −1,88)],
    [*−0,037 (t = −1,98)*],
    [−0,022 (t = −0,85)],
    [IWM],
    [−0,029 (t = −1,86)],
    [*−0,032 (t = −1,94)*],
    [−0,023 (t = −0,94)],
    [DIA],
    [−0,040 (t = −1,39)],
    [−0,042 (t = −1,52)],
    [−0,051 (t = −0,70)],
)

Comment lire ce tableau, en trois constats. Le premier est que *la nuit seule porte tout le signal*, sa statistique de Student étant partout au moins aussi grande que celle du signal complet. Le deuxième est que la première demi-heure de bourse, prise seule, ne dit rien : sa statistique ne dépasse jamais 1,2 en valeur absolue. Le troisième est ce que cela fait au nom. Ce qui subsiste sur cette fenêtre n'est pas un effet « intrajournalier » mais un lien entre l'écart d'ouverture et la clôture. Les deux n'appellent pas la même explication. Une limite subsiste : les trois régressions sont séparées, donc le tableau ne dit pas ce que la séance ajoute une fois la nuit tenue pour acquise.

=== 5.6 Ce qui survit ne se monnaie pas

L'avant-dernière demi-heure, elle, prédit la dernière positivement sur *les huit fonds*, de médiane +0,104. C'est un effet de continuation à très court terme, plus banal que celui de l'article. Il ne résiste pas aux frais, et sur les marchés émergents il ne résiste même pas à leur absence : la stratégie y rend −0,18 % par an à coût nul.

#table(
  columns: 5,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Coût par passage*],
    [*SPY*],
    [*QQQ*],
    [*IWM*],
    [*DIA*],
    [0],
    [+1,2 %],
    [+1,3 %],
    [+0,3 %],
    [+2,5 %],
    [0,25 pb],
    [−0,1 %],
    [+0,1 %],
    [−1,0 %],
    [+1,3 %],
    [0,50 pb],
    [−1,3 %],
    [−1,2 %],
    [−2,2 %],
    [+0,1 %],
    [1 pb],
    [−3,8 %],
    [−3,7 %],
    [−4,7 %],
    [−2,4 %],
)

Comment lire ce tableau, en trois constats. Le premier est que le seuil de rentabilité, le coût par passage qui ramène le rendement moyen à zéro, vaut *de 0,06 à 0,51 point de base par passage* selon le fonds. Une position par jour en demande deux. Le deuxième est que ce seuil est du même ordre que l'écart entre les meilleurs prix acheteur et vendeur sur ces fonds, donc qu'il ne laisse rien pour l'impact ni pour la commission. Le troisième est que le meilleur des quatre, le Dow Jones, est aussi celui dont les données sont les plus lacunaires, ce qui n'incite pas à s'y fier. Le tableau porte sur quatre fonds seulement. Les quatre autres ont des seuils allant de +0,08 point de base pour l'or à −0,04 pour les marchés émergents, ce dernier perdant donc avant tout frais.

#figure(image("../results/figures/cout.png", width: 100%), caption: [Ce que devient la stratégie quand on la facture])

Comment lire cette figure : une ligne par fonds, le rendement annualisé contre le coût. Les quatre lignes passent sous zéro avant un point de base.

=== 5.7 La case retenue par l'article n'est pas remarquable dans sa matrice

Treize demi-heures donnent *78 paires* dont la première pourrait prédire la seconde. L'article en retient une. Toutes éprouvées sur le S&P 500 de 2016 à 2026 :

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Compte*],
    [*Valeur*],
    [Paires éprouvées],
    [78],
    [Au-delà de deux erreurs types],
    [*4*],
    [Attendues par le seul hasard],
    [*3,5*],
)

Comment lire ce tableau, en trois constats. Le premier est que le nombre de cases significatives est celui que le hasard donne, à un demi près : sur cette fenêtre, *rien ne dépasse le bruit* dans la matrice entière. Le deuxième est que la case de l'article, la première prédisant la treizième, y figure bien parmi les quatre, mais du mauvais côté et sans y être la plus forte. Le troisième est la portée de ce compte. Il ne dit rien contre l'article, dont l'échantillon est autre et dont la case était choisie pour une raison théorique. Il dit ce qu'il faudrait exiger d'une découverte faite sur cette fenêtre-ci.

#figure(image("../results/figures/matrice.png", width: 100%), caption: [Les 78 paires de demi-heures])

Comment lire cette figure : chaque case porte la statistique de Student de la régression d'une demi-heure sur une autre, le rouge pour une pente positive et le bleu pour une négative. Seules les cases qui dépassent deux erreurs types portent leur chiffre. Le cadre noir marque celle que l'article retient.

#figure(image("../results/figures/profil.png", width: 100%), caption: [Le rendement moyen et la volatilité de chaque demi-heure])

Comment lire cette figure : deux cadres, le rendement moyen à gauche et la volatilité à droite, tous deux en points de base. Une ligne par fonds d'indice américain, SPY, QQQ, IWM et DIA, et treize points par ligne, un par demi-heure de la séance. Les marchés émergents et les marchés développés hors Amérique sont aussi des fonds d'actions, et ne sont pas tracés ici. La première demi-heure porte le plus grand rendement moyen et la plus forte volatilité des treize, sur les quatre fonds, et c'est ce qui explique l'intérêt de la littérature pour elle. La treizième remonte en volatilité sans se distinguer en rendement moyen. La figure ne porte aucun coût de passage, et ne dit donc rien de ce que les frais retirent.

== 6. Reproduire

#raw("uv sync --locked --all-extras\nuv run pytest                 # 31 tests fermés, sans réseau ni données de marché\nuv run dmh fetch              # les huit fonds, 12 434 544 barres d'une minute en tout\nuv run dmh tout               # les neuf tableaux et les cinq figures", block: true, lang: "bash")

Le téléchargement demande une clé Alpaca, à poser dans l'environnement ou dans un fichier local que le client partagé lit. Les tests, eux, tournent sur des séances fabriquées dont chaque réponse se calcule de tête. Les chiffres des tableaux de la section 5 viennent des fichiers de #raw("results/"). Quatre autres mesures sont prises depuis les barres en cache, et portent leur statut là où elles paraissent. Ce sont la perte de séances du Dow Jones, l'effet du détachement, les écarts de veille et le compte de barres.

== 7. Limites, avec leur statut

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Limite*],
    [*Statut*],
    [Les chiffres publiés par l'article n'ont pas été obtenus],
    [mesuré ; trois chemins essayés, tous fermés, et ce dépôt teste donc les affirmations du résumé et non les coefficients],
    [Huit fonds et deux signaux font seize tests],
    [déclaré ; trois coefficients y sont significativement positifs, celui de l'or sur le signal de l'article et ceux du S&P 500 et du Nasdaq 100 sur l'avant-dernière demi-heure, et c'est l'ordre de grandeur que le hasard donne à ce compte],
    [Le Dow Jones perd 30,4 % de ses séances au filtre de complétude],
    [mesuré ; 814 séances sur 2 679, c'est le moins échangé des huit, et ses résultats sont donnés mais pas mis en avant],
    [La clôture « de la veille » est celle de la séance retenue précédente],
    [mesuré ; 144 des 1 864 lignes du Dow Jones ont une veille à plus de quatre jours, 39 à plus de sept, la pire à cinquante. En n'exigeant que la vraie veille de bourse, sa pente passe de −0,040 (t = −1,39, n = 1 864) à −0,045 (t = −1,35, n = 1 720). Sur le S&P 500 les 15 lignes concernées sont toutes des fins de semaine longues],
    [Le détachement de dividende n'est pas retiré],
    [mesuré ; le rendement de la première demi-heure traverse la nuit, donc la chute de détachement, quatre fois l'an. Sur le S&P 500 il vaut −55,16 points de base ces 41 séances-là contre +4,70 ailleurs, et les retirer déplace la pente de −0,0557 à −0,0569],
    [Le seuil de complétude est de 390 barres et non de 391],
    [mesuré ; 1 231 demi-heures sur 259 480 ont perdu une minute en cours de séance et leur prix de fin est celui d'une minute antérieure. La barre de 16 h, elle, est présente sur toutes les séances retenues des huit fonds],
    [Les bornes de tiers de la section 5.4 sont calculées sur l'échantillon entier],
    [déclaré ; les pentes publiées sont descriptives, mais les colonnes de stratégie de #raw("results/tables/conditionnement.csv") décrivent un opérateur qui aurait connu la distribution de 2026 dès 2016],
    [Les jours de récession et d'annonce macroéconomique ne sont pas testés],
    [déclaré ; le résumé les cite, et les dater demanderait un calendrier que ce dépôt n'a pas construit],
    [Le coût est modélisé comme une fraction fixe du montant],
    [déclaré ; l'impact de marché d'un ordre de clôture croît avec la taille, ce que ce modèle ignore, donc le seuil publié est un plafond optimiste],
    [La fenêtre commence en 2016],
    [mesuré ; c'est la profondeur du flux consolidé du fournisseur, et 2014-2015 manquerait pour combler l'écart avec l'échantillon de l'article],
    [Les erreurs types supposent les séances indépendantes au-delà de quelques jours],
    [déclaré ; la correction de Newey et West couvre neuf retards à 2 649 séances et huit à 1 864, par la règle 4 (n/100)^(1/4). La règle de Newey et West 1994 en donnerait huit et sept],
    [Aucun test de l'effet sur des contrats à terme],
    [déclaré ; la préimpression de 2026 citée en section 8 le fait sur le Nasdaq et n'y trouve rien non plus],
)

== 8. Crédits, licence, citation

Lei Gao, Yufeng Han, Sophia Zhengzi Li et Guofu Zhou, « Market intraday momentum », _Journal of Financial Economics_, volume 129, numéro 2, 2018, pages 394 à 414 (#link("https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414")[notice EconPapers]).

Deux points de comparaison ouverts, lus en entier.

#link("https://researchmgt.monash.edu/ws/files/519509174/494419119_oa.pdf")[Manapon Limkriangkrai, Daniel Chai et Gaoping Zheng, « Market intraday momentum: APAC evidence », _Pacific-Basin Finance Journal_ 80, 2023]. Réplication déclarée, qui trouve l'effet en Chine et au Japon, faiblement en Corée du Sud, et pas du tout à Hong Kong ni à Singapour.

#link("https://arxiv.org/abs/2605.04004")[Mathias Mesfin, « Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures », arXiv 2605.04004, mai 2026]. Préimpression non revue par les pairs, qui éprouve quatorze familles de signaux intrajournaliers sur 947 séances de contrats à terme du Nasdaq et n'en retient aucune. L'avantage brut y plafonne entre 0,07 et 1,50 point quand les frais aller-retour en coûtent 2,0.

Données de marché : flux consolidé d'Alpaca, compte gratuit, usage personnel. Aucune barre n'est redistribuée. Code sous licence MIT, texte dans #raw("LICENSE") ; rapport, README et figures sous licence CC BY 4.0, texte dans #raw("LICENSE-rapport"). Figures et client de données produits par #link("https://github.com/Guilou001/gv-fintools")[gv-fintools].

Voisinage dans le portefeuille : #link("https://github.com/Guilou001/23-fnb-levier-quotidien")[23-fnb-levier-quotidien] mesure l'érosion des fonds à levier, l'autre promesse intrajournalière du programme. #link("https://github.com/Guilou001/08-facteurs-canada")[08-facteurs-canada] pose la même question à l'échelle mensuelle : une prime publiée survit-elle à sa publication. Le rapport #raw("rapport/rapport.pdf") est engendré depuis ce README.
