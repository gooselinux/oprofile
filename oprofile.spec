Summary: System wide profiler
Name: oprofile
Version: 0.9.6
Release: 7%{?dist}
License: GPLv2
Group: Development/System
#
Source0: oprofile-%{version}.tar.gz
#FIXME a workaround until java-1.6.0-openjdk-devel is available on all archs
Source1: openjdk-include.tar.gz
Requires: binutils
Requires: which
Requires(pre): shadow-utils
Patch10: oprofile-0.4-guess2.patch
Patch63: oprofile-0.7-libs.patch
Patch83: oprofile-0.9.3-xen.patch
#Patch104: oprofile-jvmpi-lgpl.patch
#Patch105: oprofile-0.9.5-timer.patch
Patch106: oprofile-sect.patch
Patch107: oprofile-stl.patch

URL: http://oprofile.sf.net

#ExclusiveArch: %{ix86} ia64 x86_64 ppc ppc64 s390 s390x alpha alphaev6 sparcv9 sparc64 %{arm}
#If oprofile doesn't build on an arch, report it and will add ExcludeArch tag.
BuildRequires: qt3-devel
BuildRequires: libxslt
BuildRequires: docbook-style-xsl
BuildRequires: docbook-utils
BuildRequires: elinks
BuildRequires: gtk2-devel
BuildRequires: automake
BuildRequires: libtool
BuildRequires: binutils-devel
BuildRequires: popt-devel
#BuildRequires: java-devel
#BuildRequires: jpackage-utils
#BuildRequires: java-1.6.0-openjdk-devel

BuildRoot: %{_tmppath}/%{name}-root

%description
OProfile is a profiling system for systems running Linux. The
profiling runs transparently during the background, and profile data
can be collected at any time. OProfile makes use of the hardware performance
counters provided on Intel P6, and AMD Athlon family processors, and can use
the RTC for profiling on other x86 processor types.

See the HTML documentation for further details.

%package devel
Summary: Header files and libraries for developing apps which will use oprofile.
Group: Development/Libraries
Requires: oprofile = %{version}-%{release}

%description devel

Header files and libraries for developing apps which will use oprofile.

%package gui
Summary: GUI for oprofile.
Group: Development/System
Requires: oprofile = %{version}-%{release}

%description gui

The oprof_start GUI for oprofile.

%package jit
Summary: Libraries required for profiling Java and other JITed code
Group: Development/System
Requires: oprofile = %{version}-%{release}
#Requires: java >= 1.6
#Requires: jpackage-utils
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires: /etc/ld.so.conf.d

%description jit
This package includes a base JIT support library, as well as a Java
agent library.

%prep
%setup -q -n %{name}-%{version} -a1
%patch10 -p1 -b .guess2
%patch63 -p1 -b .libs
%patch106 -p1 -b .sect
%patch107 -p0 -b .stl

./autogen.sh

%build
QTDIR=%{_libdir}/qt-3.3;     export QTDIR

#The CXXFLAGS below is temporary to work around
# bugzilla #113909
CXXFLAGS=-g;     export CXXFLAGS

./configure \
--with-kernel-support \
--host=%{_host} --target=%{_target_platform} --build=%{_build} \
--program-prefix= \
--prefix=%{_prefix} \
--exec-prefix=%{_exec_prefix} \
--bindir=%{_bindir} \
--sbindir=%{_sbindir} \
--sysconfdir=%{_sysconfdir} \
--datadir=%{_datadir} \
--includedir=%{_includedir} \
--libdir=%{_libdir} \
--libexecdir=%{_libexecdir} \
--localstatedir=%{_localstatedir} \
--sharedstatedir=%{_sharedstatedir} \
--mandir=%{_mandir} \
--infodir=%{_infodir} \
--with-separate-debug-dir=/usr/lib/debug \
--enable-abi \
--with-qt-dir=$QTDIR \
--with-java=`pwd`/java-1.6.0-openjdk-1.6.0.0

make CFLAGS="$RPM_OPT_FLAGS"

#tweak the manual pages
find -path "*/doc/*.1" -exec \
    sed -i -e \
     's,/doc/oprofile/,/doc/oprofile-%{version}/,g' {} \;

%install
rm -rf ${RPM_BUILD_ROOT}

mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1

make DESTDIR=${RPM_BUILD_ROOT} install

# We want the manuals in the special doc dir, not the generic doc install dir.
# We build it in place and then move it away so it doesn't get installed
# twice. rpm can specify itself where the (versioned) docs go with the
# %doc directive.
mkdir docs.installed
mv $RPM_BUILD_ROOT%{_datadir}/doc/oprofile/* docs.installed/

#hack to make header files available
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}
install -m 755 libop/op_events.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libop/op_cpu_type.h $RPM_BUILD_ROOT/%{_includedir}
#install -m 755 libop/op_events_desc.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libop/op_config.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libop/op_sample_file.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libutil/op_types.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libutil/op_list.h $RPM_BUILD_ROOT/%{_includedir}
install -m 755 libdb/odb.h $RPM_BUILD_ROOT/%{_includedir}

#hack to make .a files available
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}
install -m 755 libop/libop.a $RPM_BUILD_ROOT/%{_libdir}
install -m 755 libdb/libodb.a $RPM_BUILD_ROOT/%{_libdir}
install -m 755 libutil/liboputil.a $RPM_BUILD_ROOT/%{_libdir}
install -m 755 libutil++/liboputil++.a $RPM_BUILD_ROOT/%{_libdir}
#install -m 755 pp/liboppp.a $RPM_BUILD_ROOT/%{_libdir}
install -m 755 libabi/libopabi.a $RPM_BUILD_ROOT/%{_libdir}

mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_libdir}/oprofile" > %{buildroot}/etc/ld.so.conf.d/oprofile-%{_arch}.conf

%clean
rm -rf ${RPM_BUILD_ROOT}

%pre
getent group oprofile >/dev/null || groupadd -r -g 16 oprofile
getent passwd oprofile >/dev/null || \
useradd -r -g oprofile -d /home/oprofile -r -u 16 -s /sbin/nologin \
    -c "Special user account to be used by OProfile" oprofile
exit 0

%files
%defattr(-,root,root)
%doc  docs.installed/*
%doc COPYING

%{_bindir}/ophelp
%{_bindir}/opimport
%{_bindir}/opannotate
%{_bindir}/opcontrol
%{_bindir}/opgprof
%{_bindir}/opreport
%{_bindir}/oprofiled
%{_bindir}/oparchive
%{_bindir}/opjitconv

%{_mandir}/man1/ophelp.1.gz
%{_mandir}/man1/opannotate.1.gz
%{_mandir}/man1/opcontrol.1.gz
%{_mandir}/man1/opgprof.1.gz
%{_mandir}/man1/opreport.1.gz
%{_mandir}/man1/oprofile.1.gz
%{_mandir}/man1/oparchive.1.gz
%{_mandir}/man1/opimport.1.gz

/usr/share/oprofile

%files devel
%defattr(-,root,root)

%{_includedir}/odb.h
%{_includedir}/op_config.h
%{_includedir}/op_cpu_type.h
%{_includedir}/op_events.h
%{_includedir}/op_list.h
%{_includedir}/op_sample_file.h
%{_includedir}/op_types.h
%{_includedir}/opagent.h

%{_libdir}/libodb.a
%{_libdir}/libop.a
%{_libdir}/libopabi.a
%{_libdir}/liboputil++.a
%{_libdir}/liboputil.a

%files gui
%defattr(-,root,root)

%{_bindir}/oprof_start

%post jit -p /sbin/ldconfig

%postun jit -p /sbin/ldconfig

%files jit
%defattr(-,root,root)

%{_libdir}/oprofile
/etc/ld.so.conf.d/*

%changelog
* Fri Jun 11 2010 Will Cohen <wcohen@redhat.com> - 0.9.6-7
- Make /usr/share/oprofile/stl.pat machine independent. Resolves: rhbz#599356

* Mon Jun 7 2010 Will Cohen <wcohen@redhat.com> - 0.9.6-6
- Include jvmti java support. rhbz #463223

* Wed May 12 2010 Will Cohen <wcohen@redhat.com> - 0.9.6-5
- Handle debuginfo section differences. rhbz #591538
- Produce a 32-bit ppc oprofile packages for java support. rhbz #463223

* Fri Dec 11 2009 Will Cohen <wcohen@redhat.com> - 0.9.6-4
- Temp disable ppc and s390.

* Fri Dec 11 2009 Will Cohen <wcohen@redhat.com> - 0.9.6-3
- Java headers for jvmti.h.

* Fri Dec 11 2009 Will Cohen <wcohen@redhat.com> - 0.9.6-2
- Clean up oprofile.spec file.

* Tue Nov 24 2009 Will Cohen <wcohen@redhat.com> - 0.9.6-1
- Rebase on OProfile 0.9.6.

* Wed Oct 21 2009 Will Cohen <wcohen@redhat.com> - 0.9.5-4
- Switch to using ExcludeArch.

* Wed Oct 7 2009 Will Cohen <wcohen@redhat.com> - 0.9.5-3
- Allow timer mode to work.
- Correct location for addditional files in man pages. Resolves: rhbz #508669

* Fri Sep 4 2009 Will Cohen <wcohen@redhat.com> - 0.9.5-2
- Bump version and rebuild.

* Mon Aug 3 2009 Will Cohen <wcohen@redhat.com> - 0.9.5-1
- Rebase on OProfile 0.9.5.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.4-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Will Cohen <wcohen@redhat.com> - 0.9.4-12
- Add shadow-utils to requires. Resolves: rhbz #501357
- Add LGPL license to provided java support. Resolves: rhbz #474666
- Correct handling of --verbose. Resolves: rhbz #454969

* Mon May 11 2009 Will Cohen <wcohen@redhat.com> - 0.9.4-9
- Assign specific UID and GID to oprofile.

* Thu Apr 23 2009 Will Cohen <wcohen@redhat.com> - 0.9.4-7
- Backport Intel Architecture Perfmon support. Resolves: rhbz #497230

* Wed Apr 8 2009 Will Cohen <wcohen@redhat.com> - 0.9.4-6
- Test for basename declaration.

* Wed Apr 8 2009 Will Cohen <wcohen@redhat.com> - 0.9.4-5
- Bump version and rebuild.

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Sep 29 2008 Dennis Gilmore <dennis@ausil.us> - 0.9.4-3
- build sparcv9 not sparc

* Mon Jul 21 2008 Will Cohen <wcohen@redhat.com> - 0.9.4-2
- Correct oprofile.spec.

* Fri Jul 17 2008 Will Cohen <wcohen@redhat.com> - 0.9.4-1
- Update to orprofile 0.9.4.

* Mon Jun 23 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-18
- Fix default location for vmlinux. rhbz #451539

* Fri Apr 04 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-17
- Use older qt3-devel. rhbz #440949

* Fri Feb 15 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-16
- Corrections for compilation with gcc-4.3.

* Fri Jan 18 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-15
- Deal with xenoprof conlficts with cell. Resolves: rhbz #250852

* Fri Jan 18 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-14
- Bump format version. Check version properly. Resolves: rhbz #394571

* Fri Jan 18 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-13
- Disable profiling in hypervisor on 970MP to prevent lost interrupts.
  Resolves: rhbz #391251

* Fri Jan 18 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-12
- Use more incluse set of kernel ranges. Resolves: rhbz #307111

* Fri Jan 18 2008 Will Cohen <wcohen@redhat.com> - 0.9.3-11
- Update AMD family 10h events to match AMD documentation Resolves: rhbz #232956

* Mon Nov 12 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-7
- Should correct missing 'test' in patch.

* Mon Oct 8 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-5
- Should be popt-devel to BuildRequires.

* Mon Oct 8 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-5
- Add popt to BuildRequires.

* Mon Oct 8 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-4
- Allow short forms of --list-events (-l)  and --dump (-d).
  Resolves: rhbz#234003.

* Tue Aug 21 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-3
- rebuild

* Tue Jul 25 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-2
- Re-enable xen patch.

* Tue Jul 17 2007 Will Cohen <wcohen@redhat.com> - 0.9.3-1
- Rebase on 0.9.3 release.
- Disable xen patch until fixed.

* Mon May 21 2007 Will Cohen <wcohen@redhat.com> - 0.9.2-9
- Fix up rpmlint complaints.

* Wed Mar 21 2007 Will Cohen <wcohen@redhat.com> - 0.9.2-8
- Add AMD family 10 support. Resolves: rhbz#232956.

* Wed Mar 21 2007 Will Cohen <wcohen@redhat.com> - 0.9.2-7
- Correct description for package.
- Correct backtrace documentation. Resolves: rhbz#214793.
- Correct race condition. Resolves: rhbz#220116.


* Wed Sep 18 2006 Will Cohen <wcohen@redhat.com> - 0.9.2-3
- Add dist tag to build.

* Wed Sep 18 2006 Will Cohen <wcohen@redhat.com> - 0.9.2-2
- Rebase on 0.9.2 release.

* Thu Aug 24 2006 Will Cohen <wcohen@redhat.com>
- Update xenoprof patch.

* Wed Jul 19 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-15
- rebuild
- remove silly release definition

* Wed Jul 12 2006 Will Cohen <wcohen@redhat.com>
- Support for Intel Woodcrest. (#183081)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-13.1.1.1
- rebuild

* Mon Jul 10 2006 Will Cohen <wcohen@redhat.com>
- Add power6 support. (#196505)

* Fri Jul 7 2006 Will Cohen <wcohen@redhat.com>
- Support for power5+. (#197728)
- Fix PPC64 events and groups. (#197895)

* Wed Jun 07 2006 Will Cohen <wcohen@redhat.com>
- Put oprof_start in to oprofile-gui.

* Wed Jun 07 2006 Will Cohen <wcohen@redhat.com> - 0.9.1-10.1.1
- Bump version and rebuild.

* Sat May 13 2006 Will Cohen <wcohen@redhat.com> - 0.9.1-9.1.1
- Add xenoprof patch.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-8.1.1
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Will Cohen <wcohen@redhat.com>
- Complete path for which and dirname in opcontrol.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-7.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Dec 22 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Dec 05 2005 Will Cohen <wcohen@redhat.com>
- Correct anon namespace issue.

* Fri Nov 11 2005 Will Cohen <wcohen@redhat.com>
- Add alpha and sparcs to exclusivearch.

* Wed Jul 19 2005 Will Cohen <wcohen@redhat.com>
- Rebase on OProfile 0.9.1.
- Add MIPS 24K files to manifest.

* Wed Jun 08 2005 Will Cohen <wcohen@redhat.com>
- Rebase on OProfile 0.9.

* Wed Apr 13 2005 Will Cohen <wcohen@redhat.com>
- Add which dependency.

* Tue Apr 05 2005 Will Cohen <wcohen@redhat.com>
- Backport ppc64 patch for synthesizing dotted symbols.

* Mon Mar 21 2005 Will Cohen <wcohen@redhat.com>
- Bump release.
- Rebase on 0.8.2 release.

* Mon Mar 14 2005 Will Cohen <wcohen@redhat.com>
- Bump rebuild with gcc4.

* Wed Feb  9 2005 Will Cohen <wcohen@redhat.com>
- Do not need -D_FORTIFY_SOURCE=2
 
* Wed Feb  9 2005 Will Cohen <wcohen@redhat.com>
- Rebuild for -D_FORTIFY_SOURCE=2
 
* Fri Oct 15 2004 Will Cohen <wcohen@redhat.com>
- Additional ppc64 support for ppc64/970.

* Thu Oct 7 2004 Will Cohen <wcohen@redhat.com>
- Correct opcontrol check for Power 4/5.

* Fri Oct 1 2004 Will Cohen <wcohen@redhat.com>
- Add support for Power 4/5 performance monitoring hardware.

* Wed Sep 22 2004 Will Cohen <wcohen@redhat.com>
- Add logic to use preferred symbol names.

* Wed Sep 15 2004 Will Cohen <wcohen@redhat.com>
- Clean up file manifests.

* Mon Sep 13 2004 Will Cohen <wcohen@redhat.com>
- Rebase on 0.8.1 release.

* Wed Jul 7 2004 Will Cohen <wcohen@redhat.com>
- Add oparchive patch.

* Mon Jun 21 2004 Will Cohen <wcohen@redhat.com>
- bump version

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May 20 2004 Will Cohen <wcohen@redhat.com>
- Eliminate AUTOMAKE and ACLOCAL definitions.
- Correct QTDIR and add oprof_start to file manifests.

* Tue May 11 2004 Will Cohen <wcohen@redhat.com>
- Remove wildcards in the file manifests.
- Correct build directory.
- Use the 0.8 release tarball.

* Tue Mar 23 2004 Will Cohen <wcohen@redhat.com>
- Bump version and rebuild.

* Mon Mar 15 2004 Will Cohen <wcohen@redhat.com>
- Correct cvs checkin.

* Thu Feb 19 2004 Will Cohen <wcohen@redhat.com>
- Use automake 1.6.

* Wed Jan 21 2004 Will Cohen <wcohen@redhat.com>
- Rebase on 8.0 cvs snapshot.

* Mon Dec 01 2003 Will Cohen <wcohen@redhat.com>
- Turn on debug info patch.

* Mon Nov 24 2003 Will Cohen <wcohen@redhat.com>
- Rebase on 7.1 cvs snapshot.

* Fri Sep 26 2003 Will Cohen <wcohen@redhat.com>
- Reenable separatedebug and filepos patch.

* Thu Sep 4 2003 Will Cohen <wcohen@redhat.com>
- Limit to i386.
- Everything but x86_64.
- Turn on x86_64.

* Mon Aug 11 2003 Will Cohen <wcohen@redhat.com>
- Add gtk2-devel to build requirements.

* Thu Aug 07 2003 Will Cohen <wcohen@redhat.com>
- adapt to 0.7cvs.

* Wed Jul 30 2003 Will Cohen <wcohen@redhat.com>
- handle sample files names with spaces.
- clean spec file.
- revise opcontrol --reset.

* Fri Jul 25 2003 Will Cohen <wcohen@redhat.com>
- Restrict PATH in opcontrol.

* Wed Jul 09 2003 Will Cohen <wcohen@redhat.com>
- Patch for testing code coverage.
- Better handling of 2.5 module information.

* Fri Jun 27 2003 Will Cohen <wcohen@redhat.com>
- move to oprofile 0.5.4 pristine tarball.

* Fri Jun 13 2003 Will Cohen <wcohen@redhat.com>
- Bitmask check.

* Wed Jun 11 2003 Will Cohen <wcohen@redhat.com>
- Update AMD events.

* Fri Jun 06 2003 Will Cohen <wcohen@redhat.com>
- Build for ppc64.

* Thu Jun 05 2003 Will Cohen <wcohen@redhat.com>
- put in s390.
- Fix includes for asserts.
- Make sure elinks is available for html to txt conversion.

* Fri May 23 2003 Will Cohen <wcohen@redhat.com>
- Avoid library name collisions.

* Thu May 22 2003 Will Cohen <wcohen@redhat.com>
- Turn on ppc build.
- Turn off ppc build.
- Package op_list.h.

* Mon May 19 2003 Will Cohen <wcohen@redhat.com>
- Correct typo.

* Thu Apr 24 2003 Will Cohen <wcohen@redhat.com>
- check min event counts.
- revised op_to_source output to avoid changing line count.
- p4event events revised.
- hammer events revised.

* Wed Apr 23 2003 Will Cohen <wcohen@redhat.com>
- re-enable ppc build.

* Wed Apr 16 2003 Will Cohen <wcohen@redhat.com>
- Use /proc/ksym for module information.
- Correct separate debuginfo handling.
- Configure with --enable-abi.

* Tue Apr 1 2003 Will Cohen <wcohen@redhat.com>
- Correct path finding for daemon and op_help.

* Mon Mar 31 2003 Will Cohen <wcohen@redhat.com>
- Fix name collisons with /usr/lib/libdb.a.

* Fri Mar 28 2003 Will Cohen <wcohen@redhat.com>
- clean up spec file.
- turn off ppc build.

* Mon Mar 24 2003 Will Cohen <wcohen@redhat.com>
- getc instead of fgetc to improve performance.

* Thu Mar 20 2003 Will Cohen <wcohen@redhat.com>
- produce oprofile-devel.

* Thu Mar 13 2003 Will Cohen <wcohen@redhat.com>
- fix opvisualise patch format.

* Wed Mar 12 2003 Will Cohen <wcohen@redhat.com>
- add cmoller changes to fix warnings in opvisualise.

* Tue Mar 11 2003 Will Cohen <wcohen@redhat.com>
- setup to build on ppc.
- turn on op_visualise for ia64.
- remove unused patches.

* Mon Mar 10 2003 Will Cohen <wcohen@redhat.com>
- re-enable op_visualise.

* Fri Mar 7 2003 Will Cohen  <wcohen@redhat.com>
- move to oprofile 0.5.1 pristine tarball.
- change libdb abi.

* Fri Feb 14 2003 Will Cohen <wcohen@redhat.com>
- Requires binutils not perl.

* Thu Feb 13 2003 Will Cohen <wcohen@redhat.com>
- correct x86_64 sys_lookup_dcookie.
- correct applications of patches.

* Mon Feb 10 2003 Will Cohen <wcohen@redhat.com>
- rebuilt.
- handle stale locks
- opcontrol rtc patch
- update manpage info

* Fri Feb 7 2003 Will Cohen <wcohen@redhat.com>
- turn on build for ppc64
- change order op_visualise searches lib directories.
- revise oprofile-0.4-deprecate patch.
- utils/oprofile kernel range check, --save, and do_dump corrections.
- update gui to use "--separate=library".

* Thu Feb 6 2003 Will Cohen <wcohen@redhat.com>
- Fix dumping.

* Fri Jan 31 2003 Will Cohen <wcohen@redhat.com>
- Syscall value for x86_64.
- Update manpage and documentation.
- Revise utils/* to deprecate old.
- Include CPU_P4_HT2 in op_help.c
- Revise how CPU_TIMER_INT handled.
- Apply cookie patch for all archs.
- Correct autogen.sh location.

* Mon Jan 27 2003 Will Cohen <wcohen@redhat.com>
- Add Hammer specific events.

* Fri Jan 24 2003 Will Cohen <wcohen@redhat.com>
- Hack to get correct syscall for ia64.
- Hack to get get timer interupt data.
- Fix doc/Makefile.am.

* Wed Jan 22 2003 Will Cohen <wcohen@redhat.com>
- Add patch for separate debug infomation.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan 16 2003 Will Cohen <wcohen@redhat.com>
- Add support for P4 HT.

* Wed Jan 15 2003 Will Cohen <wcohen@redhat.com>
- Add support for x86_64.

* Tue Jan 07 2003 Will Cohen <wcohen@redhat.com>
- Revise op_visualise patch to check opendir() results.

* Mon Jan 06 2003 Will Cohen <wcohen@redhat.com>
- Patch to fix op_visualise seg fault on startup.

* Thu Jan 02 2003 Will Cohen <wcohen@redhat.com>
- Correct argument type in daemon/oprofiled.c.
- Correct QTDIR.

* Wed Dec 18 2002 Will Cohen <wcohen@redhat.com>
- Correct reporting of interrupts in oprof_start. 

* Wed Dec 18 2002 Will Cohen <wcohen@redhat.com>
- Rebuilt against new kernel

* Fri Dec 13 2002 Will Cohen <wcohen@redhat.com>
- Use opcontrol in oprof_start.

* Thu Dec 12 2002 Will Cohen <wcohen@redhat.com>
- Correct opvisualise problem.

* Tue Dec 10 2002 Will Cohen <wcohen@redhat.com>
- Add opcontrol, op_dump, op_visualise, ia64 support,
  and debugging information.

* Fri Dec 06 2002 Will Cohen <wcohen@redhat.com>
- Change to use OProfile 0.4 release and kernel support.

* Sat Nov 30 2002 Tim Powers <timp@redhat.com> 0.3-0.20021108.1
- rebuild against current version of libbfd

* Tue Aug 06 2002 Will Cohen <wcohen@redhat.com>
- Change to avoid assumption on executable name

* Fri Aug 02 2002 Will Cohen <wcohen@redhat.com>
- Move to 0.4cvs sources.

* Mon Jul 29 2002 Will Cohen <wcohen@redhat.com>
- localize nr_counter code
- add ia64 arch
- guess path to vmlinux.

* Sun Jul 28 2002 Will Cohen <wcohen@redhat.com>
- adjust structure to fit ia64 oprofile module.

* Thu Jul 25 2002 Will Cohen <wcohen@redhat.com>
- recognize ia64 cpu and events.

* Tue Jul 23 2002 Will Cohen <wcohen@redhat.com>
- changes to turn of warning as error on ia64.

* Tue Jul 23 2002 Will Cohen <wcohen@redhat.com>
- changes to allow compilation on ia64.

* Mon Jul 22 2002 Will Cohen <wcohen@redhat.com>
- pick better Red Hat Linux default image file in /boot.

* Tue Jul 14 2002 Will Cohen <wcohen@redhat.com>
- use older OProfile 0.2 kernel<->daemon API.

* Tue Jul 11 2002 Will Cohen <wcohen@redhat.com>
- avoid oprof_start installing the oprofile module

* Tue Jul 02 2002 Will Cohen <wcohen@redhat.com>
- avoid building and installing the oprofile module

* Tue May 28 2002 Jeff Johnson <jbj@redhat.com>
- create package.
