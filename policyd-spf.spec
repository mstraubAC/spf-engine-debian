%define name    python-policyd-spf
%define version 0.5.2
%define release 1
%define prefix  %{_prefix}

Summary:       pure-Python Postfix policy daemon for SPF checking
Name:          %{name}
Version:       %{version}
Release:       %{release}
License:       GPL
Group:         Applications/System
URL:           http://www.openspf.org/Software
Source:        %{name}-%{version}.tar.gz
Packager:      Scott Kitterman <scott@kitterman.com>
BuildRoot:     /var/tmp/%{name}-root
Requires:      python
Requires:      postfix >= 2.1
BuildArch:     noarch

%description
 python-policyd-spf is a Postfix SMTPd policy engine for SPF checking.
 It is implemented in pure Python and uses the python-spf module.  The SPF
 web site is http://www.openspf.org/.  The Postfix configuration must be
 changed to check SPF.  See README.Debian or man 1 python-policyd-spf for 
 details.RPM

%prep
%setup
%build

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"

#  make directories
mkdir -p "$RPM_BUILD_ROOT"/usr/lib/policyd-spf/
mkdir -p "$RPM_BUILD_ROOT"/var/lib/policyd-spf/config
mkdir -p "$RPM_BUILD_ROOT"/var/lib/policyd-spf/data
mkdir -p "$RPM_BUILD_ROOT"/usr/sbin
mkdir -p "$RPM_BUILD_ROOT"/etc/cron.d

#  copy over files
for file in policy-spf policy-spf-clean configtest \
      setup.py policy-spfsupp.py
do
   cp "$file" "$RPM_BUILD_ROOT"/usr/lib/policy-spf/
done
cp policy-spf.conf "$RPM_BUILD_ROOT"/var/lib/policy-spf/config/
cp __default__.dist "$RPM_BUILD_ROOT"/var/lib/policy-spf/config/__default__

#  link external programs to /usr/sbin
ln -s /usr/lib/python-policy-spf/policy-spf-configtest "$RPM_BUILD_ROOT"/usr/sbin

#  set up crontab
echo '0 0 * * * nobody /usr/lib/python-policy-spf/policy-spf-clean' \
      >"$RPM_BUILD_ROOT"/etc/cron.d/policy-spf

#  replace pieces in code that need to reflect new directories
(
   cd "$RPM_BUILD_ROOT"/usr/lib/python-policy-spf/
   sed 's|^sys.path.append.*|sys.path.append("/usr/lib/policy-spf")|' \
      policy-spf >policy-spf.new && \
      cat policy-spf.new >policy-spf && \
      rm -f policy-spf.new
   sed 's|^sys.path.append.*|sys.path.append("/usr/lib/policy-spf")|' \
      policy-spf-clean >policy-spf-clean.new && \
      cat policy-spf-clean.new >policy-spf-clean && \
      rm -f policy-spf-clean.new
   sed 's|^sys.path.append.*|sys.path.append("/usr/lib/policy-spf")|' \
      policy-spf-stat >policy-spf-stat.new && \
      cat policy-spf-stat.new >policy-spf-stat && \
      rm -f policy-spf-stat.new
   sed 's|^defaultConfigFilename.*|defaultConfigFilename = \
      "/var/lib/python-policy-spf/config/policy-spf.conf"|' \
      policy-spfsupp.py >policy-spfsupp.py.new && \
      cat policy-spfsupp.py.new >policy-spfsupp.py && \
      rm -f policy-spfsupp.py.new

   cd "$RPM_BUILD_ROOT"/var/lib/policy-spf/config/
   sed 's|^spfqueryPath.*|spfqueryPath = "/usr/bin/spfquery"|' \
      policy-spf.conf | \
      sed 's|^configPath.*|configPath = "file:///var/lib/policy-spf/config"|' \
      >policy-spf.conf.new && \
      cat policy-spf.conf.new >policy-spf.conf && \
      rm -f policy-spf.conf.new
)

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"

%files
%defattr(755,root,root)
/usr/lib/policy-spf
/usr/sbin/*
%dir /var/lib/policy-spf
%dir /var/lib/policy-spf/config
%config /var/lib/policy-spf/config/policy-spf.conf
%config /var/lib/policy-spf/config/__default__
%attr(700,nobody,root) /var/lib/policy-spf/data
%doc README CHANGES TODO README-RPM
