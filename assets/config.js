/* Supabase connection for the site. The publishable key is meant to be public:
 * the database rules (supabase/setup.sql) decide what it can do.
 * Leave both empty and the site reads data/minis.json from this repo instead. */
window.SWATCHWORK_CONFIG = {
  supabaseUrl: "",
  supabaseKey: "",
};
