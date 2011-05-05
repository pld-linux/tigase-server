#!/bin/sh

. /usr/share/java-utils/java-functions
set_jvm
TIGASE_HOME=/usr/share/tigase-server
TIGASE_CONFIG="/etc/tigase-server/tigase.xml"
. /etc/tigase-server/tigase.conf

TIGASE_JAR=""
for j in ${TIGASE_HOME}/jars/tigase-server*.jar ; do
	if [ -f ${j} ] ; then
	  TIGASE_JAR=${j}
	  break
	fi
done
if [ -z ${TIGASE_JAR} ] ; then
	echo "Couldn't find tigase-server.jar."
	exit 1
fi

if [ -z "${TIGASE_CONFIG}" ] ; then
  DEF_CONF="tigase-server.xml"
  # Gentoo style config location
  if [ -f "/etc/conf.d/${DEF_CONF}" ] ; then
		TIGASE_CONFIG="/etc/conf.d/${DEF_CONF}"
  elif [ -f "/etc/${DEF_CONF}" ] ; then
		TIGASE_CONFIG="/etc/${DEF_CONF}"
  elif [ -f "/etc/tigase/${DEF_CONF}" ] ; then
		TIGASE_CONFIG="/etc/tigase/${DEF_CONF}"
  elif [ -f "${TIGASE_HOME}/etc/${DEF_CONF}" ] ; then
		TIGASE_CONFIG="${TIGASE_HOME}/etc/${DEF_CONF}"
  else
		TIGASE_CONFIG="${TIGASE_HOME}/etc/${DEF_CONF}"
		echo "Can't find server configuration file."
		echo "Should be set in TIGASE_CONFIG variable"
		echo "Creating new configuration file in location:"
		echo "${TIGASE_CONFIG}"
  fi
fi

[[ -z "${TIGASE_RUN}" ]] && \
  TIGASE_RUN="tigase.server.XMPPServer -c ${TIGASE_CONFIG}  ${TIGASE_OPTIONS}"

[[ -z "${JAVA}" ]] && JAVA="${JAVA_HOME}/bin/java"

[[ -z "${CLASSPATH}" ]] || CLASSPATH="${CLASSPATH}:"

CLASSPATH="${CLASSPATH}${TIGASE_JAR}"

CLASSPATH="`ls -d ${TIGASE_HOME}/libs/*.jar 2>/dev/null | grep -v wrapper | tr '\n' :`${CLASSPATH}"

TIGASE_CMD="${JAVA} ${JAVA_OPTIONS} -cp ${CLASSPATH} ${TIGASE_RUN}"

if [ `id -u` = 0 ] ; then
	TIGASE_CMD="/sbin/setuidgid -s jabber $TIGASE_CMD"
fi

if [ -n "${TIGASE_CONSOLE_LOG}" ] ; then
	exec >> ${TIGASE_CONSOLE_LOG} 2>&1
	echo "STARTED Tigase `date`"
fi

cd "${TIGASE_HOME}"

echo "$$" > /var/run/tigase-server.pid
exec $TIGASE_CMD 
