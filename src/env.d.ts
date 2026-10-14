interface ImportMetaEnv {
	/** Google Analytics 4 measurement ID, e.g. "G-XXXXXXXXXX". */
	readonly PUBLIC_GA_MEASUREMENT_ID?: string;
	/** Google Search Console HTML-tag verification token (the `content` value only). */
	readonly PUBLIC_GOOGLE_SITE_VERIFICATION?: string;
	/** Bing Webmaster Tools `msvalidate.01` verification token. */
	readonly PUBLIC_BING_SITE_VERIFICATION?: string;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
