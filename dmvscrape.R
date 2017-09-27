require(rvest)
require(dplyr)
require(purrr)

#Takes a list, removes the empty extra BS and the carriage returns etc
clearExtra <- function(l) {
  tmp <- gsub('[\r\n\t]', '', l) %>% trimws %>% str_split(' ')
  empties <- tmp %>% lapply(function(x) x != '')
  final <- map2(.x = tmp, .y = empties, ~.x[which(.y)]) %>% sapply(paste, collapse = ' ')
}

#dmv_home <- read_html('http://wisconsindot.gov/Pages/online-srvcs/find-dmv/default.aspx')

#targets <- html_nodes(dmv_home, '.ms-rteTable-default') %>% html_nodes('td') %>% html_children %>% html_attrs
targets <- unlist(targets)
names(targets) <- gsub('^.*(city|county)=(.*)$', '\\2', t)

#pages <- lapply(targets, read_html)

addrs <- lapply(pages, html_nodes, '#stationAddressDiv') %>% lapply(html_text)
names(addrs) <- names(targets)
addrs <- addrs[sapply(addrs, length) != 0] #prune the couple of counties that have a different format
addrs.vec <- clearExtra(addrs)
#We can call geocode on the elements of addrs.vec to plot the actual location of DMV branches

#Now we get back to grabbing hours

hours <- lapply(pages, html_nodes, '#hoursDiv') %>% lapply(html_nodes, 'li')
names(hours) <- names(targets)
hours <- hours[sapply(hours, length) != 0]
hours <- lapply(hours, html_text)
hours.list <- lapply(hours, clearExtra)