# Frontend

Documentation astro : [Astro](https://docs.astro.build/)
Le style du site est fait avec TailwindCSS : [TailwindCSS](https://tailwindcss.com/)

## Installation

1. Installer les dépendances

```bash
npm install

2. Copier le fichier exemple.env et créer un fichier .env en adaptant les valeurs dans le dossier `frontend`

```

2. Lancer le serveur de développement

```bash
npm run dev
```

## Architecture

- `src` : Contient les fichiers sources
- `public` : Contient les fichiers publics
- `dist` : Contient les fichiers de production
- `node_modules` : Contient les dépendances
- `package.json` : Contient les informations du projet
- `tsconfig.json` : Contient la configuration de TypeScript
- `tailwind.config.js` : Contient la configuration de TailwindCSS

## Build

À savoir qu'Astro génère des fichiers statiques, il n'y a pas besoin de serveur pour servir le site, il suffit de servir les fichiers statiques, ils sont dans le dossier `dist`.

1. Build le site

```bash
npm run build
```

2. Servir le site

```bash
npm run start
```
