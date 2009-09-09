Epoch: 0

%define gcj_support             1
%define section                 free
%define eclipse_name            eclipse
%define version_major           0
%define version_minor           2
%define version_majmin          %{version_major}.%{version_minor}
%define version_micro           4
%define eclipse_base            %{_datadir}/%{eclipse_name}
%define eclipse_lib_base        %{_libdir}/%{eclipse_name}

# All archs line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch    %{_arch}
%endif

Summary:        Bugzilla bug tracking integration for Eclipse
Name:           %{eclipse_name}-bugzilla
Version:        %{version_majmin}.%{version_micro}
Release:        %mkrel 3.4
License:        CPL
Group:          Development/Java
#URL:                
Requires:       eclipse-platform >= 1:3.2.0
#Requires:      eclipse-platform <= 1:3.2.0

Requires:       xmlrpc >= 0:2.0.1

# Note that following the Eclipse Releng process we do not distribute a 
# real .tar.gz file.  Instead, you must build it by hand.  The way to do 
# this is to check out org.eclipse.team.bugzilla.releng.  Edit maps/bugzilla.map 
# to refer to the tag appropriate to the release.  Then run the "fetch" 
# target to fetch everything.  Package this up, such that the tar
# file unpacks a new "org.eclipse.team.bugzilla.releng" directory with all the
# contents. 
# Here's an example of how to invoke that command from within the releng 
# directory:
#
# java -cp /usr/share/eclipse/startup.jar  -Duser.home=/tmp/buildhome 
#     org.eclipse.core.launcher.Main -application org.eclipse.ant.core.antRunner 
#     -buildfile build.xml -Dbasedir=`pwd` 
#     -Dpde.build.scripts=/usr/share/eclipse/plugins/org.eclipse.pde.build_3.1.2/scripts/
#     -DdontUnzip=true fetch 
Source0:        eclipse-bugzilla-fetched-%{version_majmin}.%{version_micro}.tar.bz2

BuildRequires:  ant
BuildRequires:  eclipse-platform
BuildRequires:  eclipse-jdt
BuildRequires:  eclipse-pde
BuildRequires:  java-rpmbuild
BuildRequires:  libswt3-gtk2
BuildRequires:  xmlrpc >= 0:2.0.1

%if %{gcj_support}
BuildRequires:  gcc-java >= 0:4.0.1
BuildRequires:  java-gcj-compat-devel >= 0:1.0.31
Requires(post): java-gcj-compat >= 0:1.0.31
Requires(postun): java-gcj-compat >= 0:1.0.31
%else
BuildRequires:  java >= 0:1.4.2
BuildRequires:  java-devel >= 0:1.4.2
%endif

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The eclipse-bugzilla package contains Eclipse features and plugins for
Bugzilla bug tracking integration.

%prep
%setup -q -c 

# Change .jar to symlink for the build
pushd org.eclipse.team.bugzilla.releng/results/
rm -f plugins/org.eclipse.team.bugzilla/lib/xmlrpc.jar
ln -sf %{_datadir}/java/xmlrpc.jar plugins/org.eclipse.team.bugzilla/lib/xmlrpc.jar
rm -f plugins/org.eclipse.team.bugzilla/lib/jakarta-commons-codec.jar
ln -sf %{_datadir}/java/jakarta-commons-codec.jar plugins/org.eclipse.team.bugzilla/lib/jakarta-commons-codec.jar
popd

%build

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
SDK=$(cd SDK && pwd)

mkdir home

homedir=$(cd home > /dev/null && pwd)

pushd `pwd` 
cd org.eclipse.team.bugzilla.releng

# Call eclipse headless to process bugzilla releng build scripts
# need -Dosgi.install.area for http://gcc.gnu.org/bugzilla/show_bug.cgi?id=20198
%{java} -cp %{eclipse_base}/startup.jar                \
    -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration \
    -Duser.home=$homedir \
    -Dosgi.install.area=%{eclipse_base} \
     org.eclipse.core.launcher.Main \
    -application org.eclipse.ant.core.antRunner \
    -DjavacFailOnError=false \
    -DdontUnzip=true \
    -DbaseLocation=$SDK \
    -Dpde.build.scripts=$(echo $SDK/plugins/org.eclipse.pde.build_*)/scripts \
    -DdontFetchAnything=true 
popd

%install
rm -rf ${RPM_BUILD_ROOT}

install -d -m755 ${RPM_BUILD_ROOT}/%{eclipse_base}

# Dump the files from the releng tarball into the build root
for file in $(pwd)/org.eclipse.team.bugzilla.releng/results/I.*/*.tar.gz; do
  case $file in
    *org.eclipse.team.bugzilla*)
      # The ".." is needed since the zip files contain "eclipse/foo".
      (cd $RPM_BUILD_ROOT/%{eclipse_base}/.. && tar zxf $file)
      ;;
  esac
done

pushd $RPM_BUILD_ROOT%{_datadir}/%{eclipse_name}
rm -rf plugins/org.eclipse.team.bugzilla_%{version_majmin}.%{version_micro}/lib/xmlrpc.jar
ln -sf %{_datadir}/java/xmlrpc.jar plugins/org.eclipse.team.bugzilla_%{version_majmin}.%{version_micro}/lib/xmlrpc.jar
rm -f plugins/org.eclipse.team.bugzilla_%{version_majmin}.%{version_micro}/lib/jakarta-commons-codec.jar
ln -sf %{_datadir}/java/jakarta-commons-codec.jar plugins/org.eclipse.team.bugzilla_%{version_majmin}.%{version_micro}/lib/jakarta-commons-codec.jar
popd

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean 
rm -rf ${RPM_BUILD_ROOT}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%{eclipse_base}/features/org.eclipse.team.bugzilla*
%{eclipse_base}/plugins/org.eclipse.team.bugzilla*
%{eclipse_base}/plugins/org.eclipse.team.bugs*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif


