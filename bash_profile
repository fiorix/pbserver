# xpbcopy and xpbpaste
pbserver=http://xpb.cyclone.io

function xpbcopy() {
  tmp=/tmp/xpbcopy.$$
  trap "rm -f ${tmp}" EXIT
  IFS=$"\n" cat "${1:-/dev/stdin}" > $tmp
  if [[ -x `which curl` ]]; then curl --data-binary @${tmp} ${pbserver}
  elif [[ -x `which wget` ]]; then wget --post-file=${tmp} -qO- ${pbserver}
  else
    echo "xpbcopy requires curl or wget"
    exit 1
  fi
}

function xpbpaste() {
  pbserver=${pbserver}/$1
  if [[ -x `which curl` ]]; then curl ${pbserver}
  elif [[ -x `which wget` ]]; then wget -qO- ${pbserver}
  else
    echo "xpbpaste requires curl or wget"
    exit 1
  fi
}
