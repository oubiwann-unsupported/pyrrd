. ./admin/defs.sh
. ./admin/branchDefs.sh
echo "Preparing branch $BZR ..."
bzr init
bzr push $BZR
bzr bind $BZR
bzr cia-project $NAME
