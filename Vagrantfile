# -*- mode: ruby -*-
# vi: set ft=ruby :

plugins = %w{ vagrant-vbguest }

plugins.each do |plugin|
  unless Vagrant.has_plugin?(plugin)
      system("vagrant plugin install #{plugin}") || exit!
      exit system('vagrant', *ARGV)
  end
end

# Minimum vagrant version
Vagrant.require_version '>= 1.7.2'

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "kali-rolling"

  config.vm.provider "virtualbox" do |v, override|
    v.name = 'kali-rolling'
    v.memory = ENV['VAGRANT_MEMORY'] || 4096
    v.cpus = ENV['VAGRANT_CPUS'] || 2
  end

  config.vbguest.auto_update = true

  config.vm.provision "shell", path: 'scripts/bootstrap.sh'

end
