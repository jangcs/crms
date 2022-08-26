import crms

#args = crms.arg_parse()
#crms.crms(args)
crms.crms_list_api()
crms.crms_conf_api("git@github.com:jangcs/model_t.git", "gs://cr-model/model_t")
