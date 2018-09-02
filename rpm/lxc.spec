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
Release:        %{?prerel:0.}0.2%{?prerel:.%{prerel}}%{?dist}
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
%config(noreplace) %{_sysconfdir}/%{name}/default.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
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

%changelog
* Thu Aug 16 2018 Franz-Josef Haider <f_haider@gmx.at> 3.0.1
- Package 3.0.1 version of lxc.

* Wed May 02 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.1.1-0.2
- Rebuild for Fedora 28

* Wed Oct 25 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.1.1-0.1
- Update to 2.1.1.


* Wed Sep 27 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.1.0-0.1
- Update to 2.1.0.
- Add setuptools dependency for EPEL 7 builds

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-2.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jun 10 2017 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.8-2
- Fix for EL6 build failure.
- Fix bash completion on epel6 (rhbz#1408173).

* Tue Jun  6 2017 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.8-1
- Update to 2.0.8.

* Thu Mar  9 2017 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.7-2
- Add fix for CVE-2017-5985.

* Wed Feb 15 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.0.7-1.2
- Rebuild for brp-python-bytecompile

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.7-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Jan 29 2017 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.7-1
- Update to 2.0.7.

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 2.0.6-2.1
- Rebuild for Python 3.6

* Sun Dec  4 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.6-2
- Enable python3 on epel7 builds.
- Fix dependency on network-online.target for lxc-net.service.

* Sat Dec  3 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.6-1
- Update to 2.0.6.

* Wed Oct  5 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.5-1
- Update to 2.0.5.

* Tue Aug 16 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.4-1
- Update to 2.0.4.
- Remove conditional for eol'ed Fedora releases.

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-1.1
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Jun 29 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.3-1
- Update to 2.0.3.
- Merge spec file cleanups by Thierry Vignaud (tvignaud@redhat.com).

* Fri Jun  3 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.1-1
- Update to 2.0.1.
- Remove patch no longer needed.

* Wed Apr 20 2016 Thomas Moschny <thomas.moschny@gmx.de> - 2.0.0-1
- Update to 2.0.0.
- Obsolete the -extra subpackage.
- Move the completion file to %%{_datadir}.

* Tue Mar  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 1.1.5-2
- Power64 and s390(x) now have libseccomp support

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.5-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Nov 15 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.5-1
- Update to 1.1.5.
- Update patch.

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.4-2.1
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Wed Oct 21 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.4-2
- Add patch to fix bootorder (rhbz#1263612).

* Sat Oct 17 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.4-1
- Update to 1.1.4.

* Thu Oct  1 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.3-2
- Add security fix, see rhbz#1267844.

* Sat Aug 15 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.3-1
- Update to 1.1.3.
- Remove patches applied upstream.

* Sun Aug  2 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.2-2
- Add security fixes, see rhbz#1245939 and rhbz#1245941.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Apr 20 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.2-1
- Update to 1.1.2.
- Add patch to fix building of the lua bindings.

* Tue Mar 17 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.1-2
- Use %%license only where possible.

* Tue Mar 17 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.1-1
- Update to 1.1.1.
- Add dependency on rsync (rhbz#1177981).
- Tag COPYING with %%licence.

* Mon Feb 16 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1.1.0-3
- aarch64 now has seccomp support

* Tue Feb 10 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.0-2
- lxc-top no longer relies on the lua bindings.
- lxc-device no longer relies on the python3 bindings.
- Spec file cleanups.

* Sun Feb  8 2015 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.0-1
- Update to 1.1.0.

* Sat Aug 30 2014 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.0-0.3.alpha1
- Add missing dependency on lua-alt-getopt (rhbz#1131707).

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-0.2.alpha1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug 11 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.0-0.2.alpha1
- Fixed build dependencies on s390(x) and ppc(64(le))

* Sun Aug 10 2014 Thomas Moschny <thomas.moschny@gmx.de> - 1.1.0-0.1.alpha1
- Update to 1.1.0.alpha1.

* Fri Aug  8 2014 Thomas Moschny <thomas.moschny@gmx.de> - 1.0.5-2
- Include sysvinit resp. systemd support for autostart of containers.
- Do not list explicit requirements for templates.
- Add missing dependency on lxc-lua for lxc-top.
- Include apidocs.

* Fri Aug  8 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.5-1
- Update to 1.0.5

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jun  4 2014 Thomas Moschny <thomas.moschny@gmx.de> - 1.0.3-1
- Update to 1.0.3.
- Remove obsolete patches.
- Add systemd support.
- Lua bindings are not optional (needed e.g. for lxc-top).

* Wed May 28 2014 Kalev Lember <kalevlember@gmail.com> - 0.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Thu Jan 30 2014 Marek Goldmann <mgoldman@redhat.com> - 0.9.0-3
- There is still no Python 3 available in EPEL 7

* Wed Sep  4 2013 Thomas Moschny <thomas.moschny@gmx.de> - 0.9.0-2
- Small fix to the included Fedora template.

* Sun Sep  1 2013 Thomas Moschny <thomas.moschny@gmx.de> - 0.9.0-1
- Update to 0.9.0.
- Make the -libs subpackage installable on its own:
  - Move files needed by the libraries to the subpackage.
  - Let packages depend on -libs.
- Add rsync as dependency to the templates package.
- Add (optional) subpackages for Python3 and Lua bindings.
- Add upstream patches for the Fedora template.
- Define and use the _pkgdocdir macro, also fixing rhbz#1001235.
- Update License tag.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Mar  2 2013 Thomas Moschny <thomas.moschny@gmx.de> - 0.8.0-2
- Add upstream patch fixing the release url in the Fedora template.

* Fri Feb 15 2013 Thomas Moschny <thomas.moschny@gmx.de> - 0.8.0-1
- Update to 0.8.0.
- Modernize spec file.
- Include more templates.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Mar 26 2012 Thomas Moschny <thomas.moschny@gmx.de> - 0.7.5-1
- Update to upstream 0.7.5
- No need to run autogen.sh
- Fix: kernel header asm/unistd.h was not found
- Specfile cleanups

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jul 06 2011 Adam Miller <maxamillion@fedoraproject.org> - 0.7.4.2-1
- Update to upstream 0.7.4.2

* Fri Mar 25 2011 Silas Sewell <silas@sewell.ch> - 0.7.4.1-1
- Update to 0.7.4.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jul 26 2010 Silas Sewell <silas@sewell.ch> - 0.7.2-1
- Update to 0.7.2
- Remove templates

* Tue Jul 06 2010 Silas Sewell <silas@sewell.ch> - 0.7.1-1
- Update to 0.7.1

* Wed Feb 17 2010 Silas Sewell <silas@sewell.ch> - 0.6.5-1
- Update to latest release
- Add /var/lib/lxc directory
- Patch for sys/stat.h

* Fri Nov 27 2009 Silas Sewell <silas@sewell.ch> - 0.6.4-1
- Update to latest release
- Add documentation sub-package

* Mon Jul 27 2009 Silas Sewell <silas@sewell.ch> - 0.6.3-2
- Apply patch for rawhide kernel

* Sat Jul 25 2009 Silas Sewell <silas@sewell.ch> - 0.6.3-1
- Initial package
