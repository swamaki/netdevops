user_color=$(tput setaf 6); #cyan
host_color=$(tput setaf 2); #green
dir_color=$(tput setaf 3);  #yellow
bold=$(tput bold);
reset=$(tput sgr0);

PS1="\[${bold}\]\n";
PS1+="\[${user_color}\]\u";
PS1+="\[${reset}\]@";
PS1+="\[${host_color}\]\h:";
PS1+="\[${reset}\] in ";
PS1+="\[${dir_color}\]\W";
PS1+="\n";
PS1+="\[${reset}\]\$ \[${reset}\]"; # '$' and reset color
export PS1;
