#
# TODO:
#	- build from sources
#
Summary:	Open Source Jabber/XMPP Server
Name:		tigase-server
Version:	5.0.0
%define	build_id 2135
Release:	0.2
License:	GPL v3
Group:		Applications/Communications
# http://www.tigase.org/content/tigase-downloads?fid=2199
Source0:	%{name}-%{version}-b%{build_id}.tar.gz
# Source0-md5:	e8d305ba1ec59ac7c822c38db6169a7f
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.upstart
Source4:	derby-db-create.sh
Patch0:		%{name}-paths.patch
Patch1:		%{name}-start_script.patch
URL:		http://www.tigase.org/
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
Requires:	jpackage-utils
Requires:	jre
Requires:	rc-scripts
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


%prep
%setup -q -n %{name}-%{version}-b%{build_id}
%patch0 -p1
%patch1 -p1

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{init,sysconfig,rc.d/init.d},%{_bindir}} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/scripts \
	$RPM_BUILD_ROOT/var/lib/%{name}/{derby,scripts} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/var/log}/%{name}

cp -R certs etc/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
ln -s %{_sysconfdir}/%{name}/certs $RPM_BUILD_ROOT%{_datadir}/%{name}

cp -R database jars libs $RPM_BUILD_ROOT%{_datadir}/%{name}

install scripts/tigase.sh $RPM_BUILD_ROOT%{_bindir}/tigase-server

ln -s /var/log/tigase $RPM_BUILD_ROOT%{_datadir}/%{name}/logs
ln -s logs/derby.log $RPM_BUILD_ROOT%{_datadir}/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/init/%{name}.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{_datadir}/%{name}/scripts/derby-db-create.sh


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
%doc ChangeLog README package.html docs/api scripts/repo.sh
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/init.properties
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/tigase.conf
%dir %{_sysconfdir}/%{name}/certs
%attr(770,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/certs/*
%attr(755,root,root) %{_bindir}/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/certs
%dir %{_datadir}/%{name}/database
%{_datadir}/%{name}/database/*
%{_datadir}/%{name}/derby.log
%dir %{_datadir}/%{name}/jars
%{_datadir}/%{name}/jars/*.jar
%dir %{_datadir}/%{name}/libs
%{_datadir}/%{name}/libs/*.jar
%{_datadir}/%{name}/logs
%dir %{_datadir}/%{name}/scripts
%attr(755,root,root) %{_datadir}/%{name}/scripts/*.sh
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %attr(775,root,jabber) /var/log/%{name}
%attr(664,jabber,jabber) /var/log/%{name}/derby.log
%dir %attr(775,root,jabber) /var/lib/%{name}

%files upstart
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/init/%{name}.conf
