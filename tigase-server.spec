#
# TODO:
#	- fix with_javadoc
#	- fix with_tests (if the test are usable)
#	- use external derby and groovy (make the packages first)
#
# Conditional build:
%bcond_with	javadoc		# build javadoc
%bcond_without	source		# don't build source jar
%bcond_with	tests		# build and run tests

%include	/usr/lib/rpm/macros.java

Summary:	Open Source Jabber/XMPP Server
Name:		tigase-server
Version:	5.1.0
%define	build_id 2667
%define beta	beta3
Release:	0.%{beta}.0.1
License:	GPL v3
Group:		Applications/Communications
Source0:	https://projects.tigase.org/attachments/download/52/%{name}-%{version}-%{beta}-b%{build_id}.src.tar.gz
# Source0-md5:	c0dd6e8023b4f45559d15a603fcf8e4a
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.upstart
Source4:	derby-db-create.sh
Patch0:		%{name}-no_bash.patch
Patch1:		%{name}-paths.patch
Patch2:		%{name}-start_script.patch
Patch3:		%{name}-no_svnversion.patch
URL:		http://www.tigase.org/
%{?with_tests:BuildRequires:	ant-junit}
BuildRequires:	java-tigase-utils
BuildRequires:	java-tigase-xmltools
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Provides:	group(jabber)
Provides:	user(jabber)
Requires(post,preun):	/sbin/chkconfig
Requires:	java-tigase-utils
Requires:	java-tigase-xmltools
Requires:	jpackage-utils
Requires:	jre
Requires:	rc-scripts >= 0.4.3.0
Suggests:	java-jdbc-mysql
Suggests:	postgresql-jdbc
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Tigase Jabber/XMPP Server is Open Source and Free (GPLv3) Java
based server.

The server offers complete implementation of the XMPP protocol with a
long list of extensions. Effcient, reliable and very extensible can be
easily integrated it with your systems.

The unique features of the Tigase server are:

- High performance and scalability. Was tested with up to 500 000
  concurrent users connected to a single machine.
- High reliability. Tries to run as long as possible and tried to
  automaticaly recover from detected problems.
- Built-in many self monitoring functions. You can check your systems
  statistics via XMPP, JMX, HTTP, SNMP or you can automatically receive
  notifications about possible problems.
- Scripting support - scripts can be loaded/reloaded at run time. Many
  scripting languages are supported
- Virtual hosts support. You can have virtually unlimited virtual
  hosts which can be added/removed at runtime. You can temporarily block
  vhost or limit number of users per vhost.
- There is much more... check the official change log and the project
  website.

%package upstart
Summary:	Upstart job description for %{name}
Summary(pl.UTF-8):	Opis zadania Upstart dla %{name}
Group:		Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	upstart >= 0.6

%description upstart
Upstart job description for %{name}

%description upstart -l pl.UTF-8
Opis zadania Upstart dla %{name}

%package javadoc
Summary:	Online manual for %{name}
Summary(pl.UTF-8):	Dokumentacja online do %{name}
Group:		Documentation
Requires:	jpackage-utils

%description javadoc
Documentation for %{name}.

%description javadoc -l pl.UTF-8
Dokumentacja do %{name}.

%description javadoc -l fr.UTF-8
Javadoc pour %{name}.

%package source
Summary:	Source code of %{name}
Summary(pl.UTF-8):	Kod źródłowy %{name}
Group:		Documentation
Requires:	jpackage-utils >= 1.7.5-2

%description source
Source code of %{name}.

%description source -l pl.UTF-8
Kod źródłowy %{name}.

%prep
%setup -q -n %{name}-%{version}-%{beta}-b%{build_id}.src
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

echo "build-no=%{build_id}" >> build.properties


%build
export JAVA_HOME="%{java_home}"

required_jars="%{?with_tests:junit} tigase-xmltools tigase-utils"
CLASSPATH=$(build-classpath $required_jars)
export CLASSPATH

%ant prepare-dist jar-dist

%if %{with tests}
%ant run-unittests
%endif

%if %{with javadoc}
%ant docs
%endif

%if %{with source}
cd src
%jar cf ../%{name}.src.jar $(find -name '*.java')
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{init,sysconfig,rc.d/init.d},%{_bindir}} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/{scripts,bin,libs,jars} \
	$RPM_BUILD_ROOT/var/lib/%{name}/{derby,scripts} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/var/log}/%{name}

# jars
cp -a jars/%{name}.jar $RPM_BUILD_ROOT%{_datadir}/%{name}/jars/%{name}.jar

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -a docs-%{name}/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink
%endif

# source
%if %{with source}
install -d $RPM_BUILD_ROOT%{_javasrcdir}
cp -a %{name}.src.jar $RPM_BUILD_ROOT%{_javasrcdir}/%{name}.src.jar
%endif

cp -R certs etc/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
rm $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/init-debian.properties
rm $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/init-mysql.properties
rm $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/tigase-mysql.conf
rm $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/tigase-pgsql.conf

cp -R database $RPM_BUILD_ROOT%{_datadir}/%{name}
install libs/{derby.jar,groovy-all-*.jar,derbytools.jar,groovy-engine.jar} \
		$RPM_BUILD_ROOT%{_datadir}/%{name}/libs

install scripts/tigase.sh $RPM_BUILD_ROOT%{_bindir}/tigase-server
install scripts/config.sh $RPM_BUILD_ROOT%{_datadir}/%{name}/bin
install scripts/derby-db-create.sh $RPM_BUILD_ROOT%{_datadir}/%{name}/bin
install scripts/machine-check.sh $RPM_BUILD_ROOT%{_datadir}/%{name}/bin

ln -s /var/log/%{name} $RPM_BUILD_ROOT%{_datadir}/%{name}/logs
ln -s logs/derby.log $RPM_BUILD_ROOT%{_datadir}/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/init/%{name}.conf

touch $RPM_BUILD_ROOT/var/log/%{name}/derby.log

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 74 jabber
%useradd -g jabber -d /home/services/jabber -u 74 -s /bin/false jabber

%post
if FQDN=$(hostname -f) ; then
	sed -i -e"s/\\\$HOST_NAME/$FQDN/g" %{_sysconfdir}/%{name}/init.properties
fi
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove jabber
	%groupremove jabber
fi

%files
%defattr(644,root,root,755)
%doc package.html scripts/{repo.sh,user_roster.sh}
%doc etc/{init-mysql.properties,tigase-mysql.conf,tigase-pgsql.conf}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/bosh-extra-headers.txt
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/cross-domain-policy.xml
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/init.properties
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/jmx.access
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/jmx.password
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/snmp.acl
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/tigase.conf
%dir %{_sysconfdir}/%{name}/certs
%attr(770,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/certs/*
%attr(755,root,root) %{_bindir}/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/database
%{_datadir}/%{name}/database/*
%{_datadir}/%{name}/derby.log
%dir %{_datadir}/%{name}/jars
%{_datadir}/%{name}/jars/*.jar
%dir %{_datadir}/%{name}/libs
%{_datadir}/%{name}/libs/*.jar
%{_datadir}/%{name}/logs
%dir %{_datadir}/%{name}/scripts
%dir %{_datadir}/%{name}/bin
%attr(755,root,root) %{_datadir}/%{name}/bin/*.sh
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %attr(775,root,jabber) /var/log/%{name}
%attr(664,jabber,jabber) /var/log/%{name}/derby.log
%dir %attr(775,root,jabber) /var/lib/%{name}

%files upstart
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/init/%{name}.conf

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{version}
%ghost %{_javadocdir}/%{name}
%endif

%if %{with source}
%files source
%defattr(644,root,root,755)
%{_javasrcdir}/%{name}.src.jar
%endif
