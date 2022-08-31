#!/bin/sh

basedir="$(realpath -e "$0" | xargs dirname)"
rootdir="$(realpath -m "$basedir/..")"

die()
{
	echo "ERROR: $*" >&2
	exit 1
}

echos()
{
	printf '%s' "$*"
}

pyboard()
{
	echo "$pyboard -d $dev $*"
	"$pyboard" -d "$dev" "$@" || die "pyboard: $pyboard failed."
}

reboot_dev()
{
	pyboard --no-follow -c 'import machine as m;m.reset()'
}

format_flash()
{
	local wd_timeout="5000"

	local cmd="import machine as m, flashbdev as f, uos as u;"
	cmd="${cmd}m.WDT(0,${wd_timeout}).feed();"
	cmd="${cmd}u.umount('/');"
	cmd="${cmd}u.VfsLfs2.mkfs(f.bdev);"
	cmd="${cmd}u.mount(u.VfsLfs2(f.bdev), '/');"
	pyboard -c "$cmd"
}

transfer()
{
	local from="$1"
	local to="$2"

	if [ -d "$from" ]; then
		pyboard -f mkdir "$to"
		for f in "$from"/*; do
			if [ "$(basename "$f")" = "__pycache__" ]; then
				continue
			fi
			transfer "$f" "$to/$(basename "$f")"
		done
		return
	fi
	pyboard -f cp "$from" "$to"
}

transfer_to_device()
{
	echo "=== transfer to device $dev ==="

	format_flash
	reboot_dev
	sleep 2
	transfer "$rootdir/bme280" :/bme280
	transfer "$basedir/micropython-i2c.py" :/example_i2c.py
	transfer "$basedir/micropython-i2c-async.py" :/example_i2c_async.py
	reboot_dev
}

dev="/dev/ttyUSB0"
pyboard="pyboard.py"

while [ $# -ge 1 ]; do
	[ "$(echos "$1" | cut -c1)" != "-" ] && break

	case "$1" in
	-h|--help)
		echo "install.sh [OPTIONS] [TARGET-UART-DEVICE]"
		echo
		echo "TARGET-UART-DEVICE:"
		echo " Target serial device. Default: /dev/ttyUSB0"
		echo
		echo "Options:"
		echo " -p|--pyboard PATH   Path to pyboard executable."
		echo "                     Default: pyboard.py"
		echo " -h|--help           Show this help."
		exit 0
		;;
	-p|--pyboard)
		shift
		pyboard="$1"
		;;
	*)
		die "Unknown option: $1"
		;;
	esac
	shift
done
if [ $# -ge 1 ]; then
	dev="$1"
	shift
fi
if [ $# -ge 1 ]; then
	die "Too many arguments."
fi

transfer_to_device
exit 0
