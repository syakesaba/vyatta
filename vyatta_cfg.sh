#!/bin/vbash
# encoding: utf-8

if [ `id -u` != 0 ];then
	echo "Run as root! \"sudo $0\""
	exit
fi

# SEE: http://wiki.het.net/wiki/Cli-shell-api

############
# Tested:
#
# [VC6.6R1]
#Linux vyatta 3.3.8-1-586-vyatta #1 SMP Wed Mar 13 10:35:45 PDT 2013 i686 GNU/Linux
############

SHELL_API="cli-shell-api"

VYATTA_CFG_SESSION=$($SHELL_API getSessionEnv $PPID)
eval $VYATTA_CFG_SESSION
SHELL_API="cli-shell-api"

$SHELL_API setupSession
$SHELL_API inSession
if [ $? -ne 0 ]; then
    echo "Error opening vyatta configuration session."
fi

SHOW="$SHELL_API showCfg "
SET=${vyatta_sbindir}/my_set
DELETE=${vyatta_sbindir}/my_delete
COPY=${vyatta_sbindir}/my_copy
MOVE=${vyatta_sbindir}/my_move
RENAME=${vyatta_sbindir}/my_rename
#ACTIVATE=${vyatta_sbindir}/my_activate
#DEACTIVATE=${vyatta_sbindir}/my_activate
COMMENT=${vyatta_sbindir}/my_comment
COMMIT=${vyatta_sbindir}/my_commit
DISCARD=${vyatta_sbindir}/my_discard
SAVE=${vyatta_sbindir}/vyatta-save-config.pl
LOAD=${vyatta_sbindir}/vyatta-load-config.pl
EXIT="$SHELL_API teardownSession"

FILENAME=$(basename $0 .sh)
case $FILENAME in
    "show")
    $SHOW $@
    $COMMIT
    $EXIT
    ;;
    "set")
    $SET $@
    $COMMIT
    $EXIT
    ;;
    "delete")
        $DELETE $@
    $COMMIT
    $EXIT
    ;;
    "copy")
    $COPY $@
    $COMMIT
    $EXIT
    ;;
    "move")
    $MOVE $@
    $COMMIT
    $EXIT
    ;;
    "rename")
        $RENAME $@
    $COMMIT
    $EXIT
    ;;
#    "activate")
#    $ACTIVATE $@
#    ;;
#    "deactivate")
#    $DEACTIVATE $@
#    ;;
    "comment")
    $COMMENT $@
    $COMMIT
    $EXIT
    ;;
#    "discard")
#    $DISCARD $@
#    ;;
    "save")
    $SAVE $@
    $EXIT
    ;;
    "load")
    $LOAD $@
    $COMMIT
    $EXIT
    ;;
#    "commit")
#    $COMMIT $@
#    ;;
    *)
    case "$1" in
        "create"|"-c"|"--create")
            echo "creating symbolic links..."
            for VYATTA_CMD in "show" "set" "delete" "copy" "move" "rename" "comment" "discard" "save" "load"
            do
            ln -T -s "$0" "$VYATTA_CMD"
                done
                $EXIT
        ;;
        "erase"|"-r"|"--erase")
            echo "erasing symbolic links..."
            for VYATTA_CMD in "show" "set" "delete" "copy" "move" "rename" "comment" "discard" "save" "load"
            do
                rm -f "$VYATTA_CMD"
            done
            $EXIT
        ;;
        "help"|"-h"|"--help")
            echo "####################### VYATTA Configuration Script"
            echo "# $0 create : create symbolic links"
            echo "# $0 erase : erase symbolic links"
            echo "# source $0 (in shell script): enter configuration mode. don't forget \$EXIT mode manually."
            echo "#######################"
            $EXIT
    ;;
    esac
    # echo "$0:config:`date`" >> /var/log/vyatta_cfg/config.date
    ;;
esac
