echo '
./go.sh -r RoutineZero -p redshift-ceppi
./go.sh -r RoutineZero -p noir-ceppi
./go.sh -r RoutineZero -p visible-ceppi
./go.sh -r RoutineZero -p blueshift-ceppi

./go.sh -r RoutineZero -p redshift-hawk
./go.sh -r RoutineZero -p noir-hawk
./go.sh -r RoutineZero -p visible-hawk
./go.sh -r RoutineZero -p blueshift-hawk

./go.sh -r RoutineZero -p blueshift-aprile
./go.sh -r RoutineZero -p redshift-aprile
./go.sh -r RoutineZero -p noir-aprile
./go.sh -r RoutineZero -p visible-aprile
' > /dev/null

# ./go.sh -r RoutineZero -p botany-species^test -g alessandrovalli
./go.sh -r RoutineZero -p visible-hawk

