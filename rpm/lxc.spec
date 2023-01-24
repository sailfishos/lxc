%bcond_without selinux
%bcond_without seccomp
%bcond_with lua
%bcond_with doc
%bcond_with python3

%if %{with lua}
%global luaver 5.1
%global lualibdir %{_libdir}/lua/%{luaver}
%global luapkgdir %{_datadir}/lua/%{luaver}
%endif

# for pre-releases
#global prerel
%global commit a467a845443054a9f75d65cf0a73bb4d5ff2ab71
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           lxc
Version:        5.0.0
Release:        1
Summary:        Linux Resource Containers
License:        LGPLv2+ and GPLv2
URL:            http://linuxcontainers.org
Source:         %{name}-%{version}.tar.bz2
BuildRequires:  meson
%if %{with doc}
BuildRequires:  docbook2X
BuildRequires:  doxygen
%endif
BuildRequires:  kernel-headers
%if %{with selinux}
BuildRequires:  libselinux-devel
%endif
%if %{with seccomp}
BuildRequires:  pkgconfig(libseccomp)
%endif
BuildRequires:  libcap-devel
%if %{with lua}
BuildRequires:  pkgconfig(lua)
%endif
%if %{with python3}
BuildRequires:  pkgconfig(python3) >= 3.2
%endif
# with_python3
BuildRequires:  pkgconfig(systemd)
# lxc-extra subpackage not needed anymore, lxc-ls has been rewriten in
# C and does not depend on the Python3 binding anymore
Provides:       lxc-extra = %{version}-%{release}
Obsoletes:      lxc-extra < 1.1.5-3
%if 0%{?prerel:1}
BuildRequires:  autoconf automake
%endif
Requires:       lxc-libs = %{version}-%{release}

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%description
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.


%package        libs
Summary:        Runtime library files for %{name}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description    libs
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-libs package contains libraries for running %{name} applications.


%if %{with python3}
%package        -n python%{python3_pkgversion}-%{name}
Summary:        Python binding for %{name}

%description    -n python%{python3_pkgversion}-%{name}
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The python%{python3_pkgversion}-%{name} package contains the Python3 binding for %{name}.

%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}_lxc\\..*\\.so
%endif



%if %{with lua}
%package        -n lua-%{name}
Summary:        Lua binding for %{name}
Requires:       lua-filesystem

%description    -n lua-%{name}
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The lua-%{name} package contains the Lua binding for %{name}.
%endif

%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}core\\.so\\.0


%package        templates
Summary:        Templates for %{name}
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
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%if %{with doc}
%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
This package contains documentation for %{name}.
%endif

%prep
%autosetup -p1 -n %{name}-%{version}/%{name}

%build
%meson \
           -Ddoc-path=%{_pkgdocdir} \
%if %{with doc}
           -Dman=true \
%else
           -Dman=false \
%endif
           -Dapparmor=true \
%if %{with selinux}
           -Dselinux=true \
%else
           -Dselinux=false \
%endif
%if %{with seccomp}
           -Dseccomp=true \
%endif
           -Dinit-script=systemd

%meson_build

%install
%meson_install
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
%if %{with lua}
chmod -x %{buildroot}%{luapkgdir}/lxc.lua
%endif

mkdir -p %{buildroot}%{_pkgdocdir}
cp -a AUTHORS %{!?_licensedir:COPYING} %{buildroot}%{_pkgdocdir}
mkdir -p %{buildroot}%{_pkgdocdir}/api
%if %{with doc}
cp -a doc/api/html/* %{buildroot}%{_pkgdocdir}/api/
%else
# Remove any doc package leftovers
rm -rf %{buildroot}%{_pkgdocdir}/examples
%endif

# cache dir
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

%if %{without selinux}
# remove selinux files? TODO
rm %{buildroot}/%{_datarootdir}/lxc/selinux/lxc.if
rm %{buildroot}/%{_datarootdir}/lxc/selinux/lxc.te
%endif

%post libs
/sbin/ldconfig
%systemd_post %{name}-net.service
%systemd_post %{name}-monitord.service
%systemd_post %{name}.service
%systemd_post %{name}@.service


%preun libs
%systemd_preun %{name}-net.service
%systemd_preun %{name}-monitord.service
%systemd_preun %{name}.service
%systemd_preun %{name}@.service


%postun libs
/sbin/ldconfig
%systemd_postun %{name}-net.service
%systemd_postun %{name}-monitord.service
%systemd_postun %{name}.service
%systemd_postun %{name}@.service


%files
%{_bindir}/%{name}-*
%exclude %{_bindir}/%{name}-autostart
%if %{with doc}
%{_mandir}/man1/%{name}*
%{_mandir}/*/man1/%{name}*
# in lxc-libs:
%exclude %{_mandir}/man1/%{name}-autostart*
%exclude %{_mandir}/*/man1/%{name}-autostart*
%exclude %{_mandir}/man1/%{name}-user-nic*
%exclude %{_mandir}/*/man1/%{name}-user-nic*
%endif
%{_datadir}/%{name}/%{name}.functions
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/_%{name}
%{_datadir}/bash-completion/completions/%{name}*

%files libs
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/templates
%dir %{_datadir}/%{name}/config
%{_datadir}/%{name}/hooks
%{_datadir}/%{name}/%{name}-patch.py*
%if %{with selinux}
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
%if %{with doc}
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
%if 0%{?_licensedir:1}
%license COPYING
%else
%{_pkgdocdir}/COPYING
%endif
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{_unitdir}/%{name}-net.service
%{_unitdir}/%{name}-monitord.service
%dir %{_localstatedir}/cache/%{name}


%if %{with python3}
%files -n python%{python3_pkgversion}-%{name}
%{python3_sitearch}/*
%endif
# with_python3


%if %{with lua}
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
%{_libdir}/liblxc.a

%if %{with doc}
%files doc
%dir %{_pkgdocdir}
# AUTHORS and COPYING intentionally duplicated because -doc
# can be installed on its own.
%{_pkgdocdir}/*
%if 0%{?_licensedir:1}
%license COPYING
%endif
%endif
