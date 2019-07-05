
Debian
====================
This directory contains files used to package cintamanid/cintamani-qt
for Debian-based Linux systems. If you compile cintamanid/cintamani-qt yourself, there are some useful files here.

## cintamani: URI support ##


cintamani-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install cintamani-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your cintamani-qt binary to `/usr/bin`
and the `../../share/pixmaps/cintamani128.png` to `/usr/share/pixmaps`

cintamani-qt.protocol (KDE)

