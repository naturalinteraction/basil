for i in 2226 2227 2228 2229
do
    printf '\n\n'
    ssh pi@$CALLALTA -p $i $@
done

printf '\n\n'
sshpass -p $BOTANY_PASSWORD ssh pi@$ORTO $@

printf '\nall done\n'

