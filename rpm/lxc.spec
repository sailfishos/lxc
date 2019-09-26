%define no_doc 1
%define no_apparmor 1
%define no_selinux 1
%global with_systemd 1
%define no_lua 1

%if %{no_lua} == 0
%global luaver 5.1
%global lualibdir %{_libdir}/lua/%{luaver}
%global luapkgdir %{_datadir}/lua/%{luaver}
%endif

%define source_dir .

# for pre-releases
#global prerel
%global commit a467a845443054a9f75d65cf0a73bb4d5ff2ab71
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           lxc
Version:        3.0.1
Release:        1
Summary:        Linux Resource Containers
Group:          Applications/System
License:        LGPLv2+ and GPLv2
URL:            http://linuxcontainers.org
Source:         %{name}-%{version}.tar.bz2
%if %{no_doc} == 0
BuildRequires:  docbook2X
BuildRequires:  doxygen
%endif
BuildRequires:  kernel-headers
%if %{no_selinux} == 0
BuildRequires:  libselinux-devel
%endif
%if 0%{?with_seccomp}
BuildRequires:  pkgconfig(libseccomp)
%endif # with_seccomp
BuildRequires:  libcap-devel
BuildRequires:  libtool
%if %{no_lua} == 0
BuildRequires:  pkgconfig(lua)
%endif
%if 0%{?with_python3}
BuildRequires:  pkgconfig(python3) >= 3.2
%if 0%{?rhel} == 7
BuildRequires:  python34-setuptools
%endif
%endif # with_python3
%if 0%{?with_systemd}
BuildRequires:  systemd
%endif # with_systemd
%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires:  pkgconfig(bash-completion)
%endif
# lxc-extra subpackage not needed anymore, lxc-ls has been rewriten in
# C and does not depend on the Python3 binding anymore
Provides:       lxc-extra = %{version}-%{release}
Obsoletes:      lxc-extra < 1.1.5-3
%if 0%{?prerel:1}
BuildRequires:  autoconf automake
%endif

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%description
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.


%package        libs
Summary:        Runtime library files for %{name}
Group:          System Environment/Libraries
# rsync is called in bdev.c, e.g. by lxc-clone
Requires:       rsync
%if 0%{?with_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): chkconfig
Requires(preun): initscripts, chkconfig
Requires(postun): initscripts
%endif # with_systemd


%description    libs
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-libs package contains libraries for running %{name} applications.


%if 0%{?with_python3}
%package        -n python%{python3_pkgversion}-%{name}
Summary:        Python binding for %{name}
Group:          System Environment/Libraries

%description    -n python%{python3_pkgversion}-%{name}
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The python%{python3_pkgversion}-%{name} package contains the Python3 binding for %{name}.

%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}_lxc\\..*\\.so
%endif # with_python3


%if %{no_lua} == 0
%package        -n lua-%{name}
Summary:        Lua binding for %{name}
Group:          System Environment/Libraries
Requires:       lua-filesystem

%description    -n lua-%{name}
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The lua-%{name} package contains the Lua binding for %{name}.
%endif

%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}core\\.so\\.0


%package        templates
Summary:        Templates for %{name}
Group:          System Environment/Libraries
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
# Note: Requirements for the template scripts (busybox, dpkg,
# debootstrap, rsync, openssh-server, dhclient, apt, pacman, zypper,
# ubuntu-cloudimg-query etc...) are not explicitly mentioned here:
# their presence varies wildly on supported Fedora/EPEL releases and
# archs, and they are in most cases needed for a single template
# only. Also, the templates normally fail graciously when such a tool
# is missing. Moving each template to its own subpackage on the other
# hand would be overkill.


%description    templates
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-templates package contains templates for creating containers.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

#%if %{no_doc} == 0
%package        doc
Summary:        Documentation for %{name}
Group:          Documentation
BuildArch:      noarch

%description    doc
This package contains documentation for %{name}.
#%endif

%prep
%setup -q -n %{name}-%{version}/%{name}

%build
CFLAGS="$CFLAGS -std=c99 -D_GNU_SOURCE"
cd %{source_dir}
autoreconf -v -f -i
%configure --with-distro=fedora \
           --disable-silent-rules \
           --docdir=%{_pkgdocdir} \
%if %{no_doc} == 0
           --enable-doc \
           --enable-api-docs \
%else
           --disable-doc \
           --disable-api-docs \
%endif
           --disable-rpath \
           --disable-apparmor \
           --disable-cgmanager \
%if %{no_selinux} == 0
           --enable-selinux \
%else
           --disable-selinux \
%endif
%if 0%{?with_seccomp}
           --enable-seccomp \
%endif # with_seccomp
%if %{no_lua} == 0
           --enable-lua \
%else
           --disable-lua \
%endif
%if 0%{?with_python3}
           --enable-python \
%else
           --disable-python \
%endif # with_python3
%if 0%{?with_systemd}
           --with-init-script=systemd \
%else
           --with-init-script=sysvinit \
%endif # with_systemd
           --disable-werror \
           --disable-static
# intentionally blank line

# fix rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
cd %{source_dir}
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
%if %{no_lua} == 0
chmod -x %{buildroot}%{luapkgdir}/lxc.lua
%endif

mkdir -p %{buildroot}%{_pkgdocdir}
cp -a AUTHORS README %{!?_licensedir:COPYING} %{buildroot}%{_pkgdocdir}
mkdir -p %{buildroot}%{_pkgdocdir}/api
%if %{no_doc} == 0
cp -a doc/api/html/* %{buildroot}%{_pkgdocdir}/api/
%endif

# cache dir
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

# remove libtool .la file
rm -rf %{buildroot}%{_libdir}/liblxc.la


%if %{no_selinux} == 1
# remove selinux files? TODO
rm %{buildroot}/%{_datarootdir}/lxc/selinux/lxc.if
rm %{buildroot}/%{_datarootdir}/lxc/selinux/lxc.te
%endif

%check
cd %{source_dir}
make check


%post libs
/sbin/ldconfig
%if 0%{?with_systemd}
%systemd_post %{name}-net.service
%systemd_post %{name}.service
%systemd_post %{name}@.service
%else
/sbin/chkconfig --add %{name}-net
/sbin/chkconfig --add %{name}
%endif # with_systemd


%preun libs
%if 0%{?with_systemd}
%systemd_preun %{name}-net.service
%systemd_preun %{name}.service
%systemd_preun %{name}@.service
%else
if [ $1 -eq 0 ]; then
        /sbin/service %{name}-net stop > /dev/null 2>&1
        /sbin/chkconfig --del %{name}-net
        /sbin/service %{name} stop > /dev/null 2>&1
        /sbin/chkconfig --del %{name}
fi
%endif # with_systemd


%postun libs
/sbin/ldconfig
%if 0%{?with_systemd}
%systemd_postun %{name}-net.service
%systemd_postun %{name}.service
%systemd_postun %{name}@.service
%else
if [ $1 -ge 1 ]; then
        /sbin/service %{name}-net condrestart > /dev/null 2>&1 || :
        /sbin/service %{name} condrestart > /dev/null 2>&1 || :
fi
%endif # with_systemd


%files
%{_bindir}/%{name}-*
%exclude %{_bindir}/%{name}-autostart
%if %{no_doc} == 0
%{_mandir}/man1/%{name}*
%{_mandir}/*/man1/%{name}*
# in lxc-libs:
%exclude %{_mandir}/man1/%{name}-autostart*
%exclude %{_mandir}/*/man1/%{name}-autostart*
%exclude %{_mandir}/man1/%{name}-user-nic*
%exclude %{_mandir}/*/man1/%{name}-user-nic*
%endif
%{_datadir}/%{name}/%{name}.functions
%if 0%{?fedora} || 0%{?rhel} >= 7
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/%{name}
%else
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/bash_completion.d/%{name}
%endif


%files libs
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/templates
%dir %{_datadir}/%{name}/config
%{_datadir}/%{name}/hooks
%{_datadir}/%{name}/%{name}-patch.py*
%if %{no_selinux} == 0
%{_datadir}/%{name}/selinux
%endif
%{_libdir}/liblxc.so.*
%{_libdir}/%{name}
%{_libexecdir}/%{name}
# fixme: should be in libexecdir?
%{_sbindir}/init.%{name}
%{_bindir}/%{name}-autostart
%{_sharedstatedir}/%{name}
%dir %{_sysconfdir}/%{name}
%config %{_sysconfdir}/%{name}/default.conf
%config %{_sysconfdir}/sysconfig/%{name}
%if %{no_doc} == 0
%{_mandir}/man1/%{name}-autostart*
%{_mandir}/*/man1/%{name}-autostart*
%{_mandir}/man1/%{name}-user-nic*
%{_mandir}/*/man1/%{name}-user-nic*
%{_mandir}/man5/%{name}*
%{_mandir}/man7/%{name}*
%{_mandir}/*/man5/%{name}*
%{_mandir}/*/man7/%{name}*
%endif
%dir %{_pkgdocdir}
%{_pkgdocdir}/AUTHORS
%{_pkgdocdir}/README
%if 0%{?_licensedir:1}
%license COPYING
%else
%{_pkgdocdir}/COPYING
%endif
%if 0%{?with_systemd}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{_unitdir}/%{name}-net.service
%else
%{_sysconfdir}/rc.d/init.d/%{name}
%{_sysconfdir}/rc.d/init.d/%{name}-net
%endif # with_systemd
%dir %{_localstatedir}/cache/%{name}


%if 0%{?with_python3}
%files -n python%{python3_pkgversion}-%{name}
%{python3_sitearch}/*
%endif # with_python3


%if %{no_lua} == 0
%files -n lua-%{name}
%{lualibdir}/%{name}
%{luapkgdir}/%{name}.lua
%endif

%files templates
%{_datadir}/%{name}/templates/lxc-*
%{_datadir}/%{name}/config/*


%files devel
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/lxc
%{_libdir}/liblxc.so

#%if %{no_doc} == 0
%files doc
%dir %{_pkgdocdir}
# README, AUTHORS and COPYING intentionally duplicated because -doc
# can be installed on its own.
%{_pkgdocdir}/*
%if 0%{?_licensedir:1}
%license COPYING
%endif
#%endif
