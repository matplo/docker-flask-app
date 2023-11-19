#!/bin/bash

savedir=${PWD}

function thisdir()
{
	SOURCE="${BASH_SOURCE[0]}"
	while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
	  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
	  SOURCE="$(readlink "$SOURCE")"
	  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
	done
	DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
	echo ${DIR}
}
THISD=$(thisdir)

cd ${THISD}

venvdir=${THISD}/appenv
cmnd=$@

first_run=""
if [ ! -d ${venvdir} ]; then
	echo "[i] creating venv"

	venv_cmnd=""
	python3 -m virtualenv -h 2>&1 >> /dev/null
	if [ "x$?" != "x0" ]; then
		echo "[w] no virtualenv - trying venv"
		python3 -m venv -h 2>&1 >> /dev/null
		if [ "x$?" != "x0" ]; then
			echo "[w] python3 -m venv -h returned $?"
		else
			venv_cmnd="venv"
		fi
	else
		venv_cmnd="virtualenv"
	fi

	if [ -z "${venv_cmnd}" ]; then
		echo "[e] do not know how to setup virtual environment... bailing out."
		exit -1
	fi

	python3 -m ${venv_cmnd} ${venvdir}
	first_run="yes"
fi

tmpfile=$(mktemp)
if [ -d ${venvdir} ]; then
	echo "export PS1=\"\e[32;1m[\u\e[31;1m@\h\e[32;1m]\e[34;1m\w\e[0m\n> \"" > ${tmpfile}
	if [ -e "$HOME/.bashrc" ]; then
		echo "source $HOME/.bashrc" >> ${tmpfile}
	fi
	if [ -e "$HOME/.bash_profile" ]; then
		echo "source $HOME/.bash_profile" >> ${tmpfile}
	fi
	echo "source ${venvdir}/bin/activate" >> ${tmpfile}
	if [ "x${first_run}" == "xyes" ]; then
		echo "[i] first run? ${first_run}"
		echo "python -m pip install --upgrade pip" >> ${tmpfile}
		echo "python -m pip install pyyaml find_libpython tqdm" >> ${tmpfile}
		echo "python -m pip install -r requirements.txt" >> ${tmpfile}
	fi
	if [ ! -e "${THISD}/.venvstartup.sh" ]; then
		echo "module list" >> ${THISD}/.venvstartup.sh
	fi
	echo "source ${THISD}/.venvstartup.sh" >> ${tmpfile}
	echo "cd ${savedir}" >> ${tmpfile}
	if [ -z "${cmnd}" ]; then
		/bin/bash --init-file ${tmpfile} -i
	else
		echo "[i] exec ${tmpfile}" >&2
		echo "${cmnd}" >> ${tmpfile}
		chmod +x ${tmpfile}
		${tmpfile}
	fi
	#-s < .activate
fi

cd ${savedir}
