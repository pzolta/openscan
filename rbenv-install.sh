#!/bin/bash
HOME='/root'
cd
git clone git://github.com/sstephenson/rbenv.git .rbenv
echo 'export PATH="/root/.rbenv/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(rbenv init -)"' >> ~/.bash_profile
git clone git://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build
echo 'export PATH="/root/.rbenv/plugins/ruby-build/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
rbenv install -v 2.2.3
rbenv global 2.2.3
ruby -v
echo "gem: --no-document" > ~/.gemrc
gem install bundler