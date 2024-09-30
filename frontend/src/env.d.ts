/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly PUBLIC_BASE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}