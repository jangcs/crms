import crms

#args = crms.arg_parse()
#crms.crms(args)
crms.crms_list_api()
crms.crms_conf_mod_api("mod@github.com:jangcs/model_t.git", "gs://cr-model_mod/model_t")
