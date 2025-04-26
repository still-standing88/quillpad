# replit.nix
{ pkgs }: {
  deps = [
    pkgs.python311Packages.pip
    pkgs.python311
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.git
    pkgs.postgresql # Provides libpq for psycopg2
    pkgs.zlib
    pkgs.libjpeg
    pkgs.gcc
    pkgs.pkg-config
  ];
}