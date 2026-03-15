fio /home/cb76/cb761228/perf-oriented-dev/solutions/IO-Loader/background_load.fio &
sleep 10

nice -n 10 $1

killall fio &> /dev/null
rm /tmp/generated_cb761228/fio_fiel.dat 