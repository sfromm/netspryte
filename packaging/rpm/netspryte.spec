Name:       netspryte
Version:	0.1
Release:	1%{?dist}
Summary:	Tool for collecting network information

License:	GPLv3
URL:		https://github.com/sfromm/netspryte
#Source0:	https://github.com/sfromm/netspryte/archive/release%{version}.tar.gz
Source0:	%{name}-%{version}.tar.gz

BuildArch:  noarch
BuildRequires:	python-devel
BuildRequires:  python-setuptools
Requires:   python-flask
Requires:   python-psycopg2
Requires:   python-pysnmp
Requires:   rrdtool-python

%description
Tool for collecting network information.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{python_sitelib}/netspryte/*
%{python_sitelib}/netspryte*egg-info
%{_bindir}/netspryte-*
%{_bindir}/rrd-*
%doc README.md COPYING

%changelog
* Mon Jun 13 2016 Stephen Fromm <sfromm gmail com>
- Initial version
