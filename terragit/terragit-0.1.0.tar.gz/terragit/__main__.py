import sys
import argparse
import terragit.terracommand as  terracommande
import terragit.terradocs as  terradocse

def main():
    # if sys.argv[1] =="docs":
    #
    #     terradoc =terradocs.terradoc("","https://gitlab.com","89A_ySPyToEV4uEE_soY")
    #     terradoc.getModule(terradoc.getSubgroupList(7516055))
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--gitlab_token",  dest = "gitlab_token",default=None , help="gitlab token")
    parser.add_argument("-u", "--gitlab_url",  dest = "gitlab_url" , default ="https://gitlab.com" ,help="gitlab url")

    if sys.argv[1] in ["changes","validate","plan","apply","output"]:
        parser.add_argument("-p", "--project_id",  dest = "project_id",default = None, help="id of project")
        parser.add_argument("-c", "--commit_id",  dest = "commit_id" ,default = None,help="id of commit")
        parser.add_argument("-dir", "--directory",  dest = "directory" ,default = None,help="directory")
        parser.add_argument("-mrid", "--mr_id", dest = "mr_id",default = None, help="merge request id")
        parser.add_argument("-ct", "--commit_title", dest = "commit_title",default = "", help="commit title")
        parser.add_argument('-v', '--verbose',action="store_true")
        parser.add_argument("-d", "--destroy",action="store_true")
        parser.add_argument(sys.argv[1])

        args = parser.parse_args()
        if args.destroy :
            if sys.argv[1] == "plan" :
                sys.argv[1] = sys.argv[1]+"-destroy"
            if sys.argv[1] == "apply" :
                sys.arg[1] = "destroy"
        comm =terracommande.terracommand(args.project_id, args.commit_id, args.mr_id, args.gitlab_token, args.gitlab_url, args.directory, args.verbose, args.commit_title)

        comm.terragruntCommand(sys.argv[1])
    if sys.argv[1] =="docs":
        parser.add_argument("-m", "--module", dest = "module",default = "", help="module")
        parser.add_argument("-o", "--output", dest = "output_path",default = "", help="output path")

        parser.add_argument(sys.argv[1])
        args = parser.parse_args()

        terradoc =terradocse.terradoc(args.output_path,args.gitlab_url,args.gitlab_token)
        subgrouplist=terradoc.getSubgroupList(args.module)
        terradoc.getModule(subgrouplist,args.module)
        terradoc.f.close()

if __name__ == '__main__':
    main()
