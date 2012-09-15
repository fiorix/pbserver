# xpbcopy and xpbpaste
xpburl=http://xpb.cyclone.io

function xpbcopy() {
  tmp=/tmp/xpbcopy.$$
  trap "rm -f ${tmp}" EXIT
  IFS=$"\n" cat "${1:-/dev/stdin}" > $tmp
  if [[ -x `which curl` ]]; then curl --data-binary @${tmp} ${xpburl}
  elif [[ -x `which wget` ]]; then wget --post-file=${tmp} -qO- ${xpburl}
  else
    echo "xpbcopy requires curl or wget"
    exit 1
  fi
}

function xpbpaste() {
  xpburl=${xpburl}/$*
  if [[ -x `which curl` ]]; then curl ${xpburl}
  elif [[ -x `which wget` ]]; then wget -qO- ${xpburl}
  else
    echo "xpbpaste requires curl or wget"
    exit 1
  fi
}
