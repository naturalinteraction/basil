batch=
group=zero
./go.sh -p redshift-$batch -s '' -d -g $group
./go.sh -p blueshift-$batch -s '' -d -g $group
./go.sh -p noir-$batch -s '' -d -g $group
./go.sh -p visible-$batch -s '' -d -g $group

batch=
group=alessandrovalli
./go.sh -p botany-$batch -d -g $group
