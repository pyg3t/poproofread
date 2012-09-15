# This makefile is used to update templates for internationalization ("i18n")
# of ag.

# INSTRUCTIONS
# ------------
#
# To update existing templates with strings from the latest python files, 
# just run 'make'.
#
# To create a translation template for a new language (e.g. de_DE.UTF8), run:
#     LANG=de_DE.UTF8 make init
# 

# List of files calling gettext.
TRANSLATIONFILES=../*.py ../gui/about_dialog.glade.h

#TRANSLATIONFILES=../ag.py ../calculator.py ../colors.py ../constraints.py ../crystal.py ../debug.py ../dft.py ../energyforces.py ../execute.py ../graphene.py ../graphs.py ../gtkexcepthook.py ../gui.py ../minimize.py ../movie.py ../nanoparticle.py ../nanotube.py ../progress.py ../pybutton.py ../quickinfo.py ../render.py ../repeat.py ../rotate.py ../scaling.py ../settings.py ../setupwindow.py ../simulation.py ../status.py ../surfaceslab.py ../widgets.py

i18n: poproofread.pot update-po compile

../gui/about_dialog.glade.h: ../gui/*.glade
	intltool-extract --type=gettext/glade ../gui/*.glade

# This will update the English template (poproofread.pot) with English messages from 
# the Python source code.
poproofread.pot: ${TRANSLATIONFILES}
	xgettext --add-comments --from-code=UTF-8 --keyword=_ --keyword=N_ --output=poproofread.pot --msgid-bugs-address=k.nielsen81@gmail.com --copyright-holder="Kenneth Nielsen" --package-name=poproofread ${TRANSLATIONFILES}

# This will create an empty translation file ($LANGUAGE.po, where $LANGUAGE is
# an environment variable) from the English template poproofread.pot.
# The po-file header will have to be edited afterwards.
init: poproofread.pot
	mkdir -p ${LANGUAGE}/LC_MESSAGES
	msginit --locale=${LANGUAGE}.UTF8 --input=poproofread.pot --output-file=${LANGUAGE}/LC_MESSAGES/poproofread.po

# This will merge new/changed English strings from the template ag.pot
# into all existing translations (*.po), maximally
# reusing the existing translations.
update-po: poproofread.pot
	for FILE in $(wildcard */LC_MESSAGES/poproofread.po); do \
	  msgmerge --previous --update $$FILE poproofread.pot ;\
	done

# This will compile all translations (*.po) into binary files in gettext's
# search directory.
compile: */LC_MESSAGES/poproofread.po
	for DIR in $(wildcard */LC_MESSAGES); do \
	  echo Checking $$DIR/poproofread.po ;\
	  msgfmt -cv --output-file=$$DIR/poproofread.mo $$DIR/poproofread.po ;\
	done
