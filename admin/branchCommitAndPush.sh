. ./admin/defs.sh
. ./admin/branchDefs.sh
./admin/commit.sh $1 && pushLaunchpad || error
pushGoogle || error
