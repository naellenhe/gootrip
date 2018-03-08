"use strict";



class ChangeProfile extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            'name': '', 
            'email': '', 
            'password': '',
            'birthyear': '',
            'zipcode': '',
        };
        this.handleUserInputChange = this.handleUserInputChange.bind(this);
    }

    componentWillMount(){
        // send AJAX to get user data, update state
        fetch('/user.json',{
                  method: 'POST',
                  headers: new Headers({
                    'Content-Type': 'application/json'
                  }),
                  body: JSON.stringify({'user_id' : user_id})
            })
            .then( (r) => r.json())
            .then( (j) => this.setState({'name': j.name, 
                                         'email': j.email,
                                         'password': j.password,
                                         'birthyear': j.birthyear,
                                         'zipcode': j.zipcode }));

    }


    handleUserInputChange(change){
        // console.log(change);
        this.setState(change);
        // console.log('current state is ', this.state);
    }


    componentDidUpdate(){
        // send AJAX to get user data, update state
        fetch('/update_user_profile.json',{
                  method: 'POST',
                  headers: new Headers({
                    'Content-Type': 'application/json'
                  }),
                  body: JSON.stringify({
                    'user_id' : user_id,
                    'name': this.state.name, 
                    'email': this.state.email, 
                    'password': this.state.password,
                    'birthyear': this.state.birthyear,
                    'zipcode': this.state.zipcode
                  })
            })
            .then( (r) => r.json())
            .then( (j) => console.log(j.msg));

    }

    render(){
        let userInfoItem = [];
        for (let item in this.state){
            let itemContent = this.state[item];
            userInfoItem.push(<UserInfo 
                                userInfo={item}
                                userInfoContent={itemContent}
                                key={item}
                                change={this.handleUserInputChange} />);
        }

        // console.log(this.state);

        let userInfoTitlesUpper = ['Name', 'Email', 'Password', 'Birthyear', 'Zipcode'];
        let userInfoTitles = ['name', 'email', 'password', 'birthyear', 'zipcode'];
        let i = 0;
        let showUserInfo = userInfoTitles.map(title => {
            i++;
            let collapseId = `collapse${i-1}`;
            let collapseIdTarget = `#collapse${i-1}`;
            return (
                <div key={i-1}>
                  <button type="button" 
                    className="list-group-item" data-toggle="collapse" 
                    data-target={collapseIdTarget} aria-expanded="false"
                    aria-controls={collapseIdTarget} style={{ "marginBottom" : "0px"}}>
                    <div className="row">

                      <div className="col-xs-3"><span><strong>{ userInfoTitlesUpper[i-1] }</strong></span></div>
                      <div className="col-xs-6"><span>{this.state[title]}</span></div>
                      <div className="col-xs-3"><UserInfoEdit href={collapseIdTarget} control={collapseId} toShowOrHide={this.state.action} /></div>

                    </div>
                  </button>
                  
                  <div className="row" >
                    <div className="collapse col-xs-8 col-xs-offset-2"id={collapseId}>
                        { userInfoItem[i-1] }
                    </div>
                  </div>
                </div>
                  
            )
          }
        );
        return (
          <div className="row">
            <div className="col-xs-10">
              <div className="panel panel-default">
                <ul className="list-group"> 
                  {showUserInfo}
                </ul>
              </div>
            </div>
          </div>
        );
    }

}


class UserInfoEdit extends React.Component {
  constructor(props) {
    super(props);

  }

  render() {
    return <span>
      <i className="glyphicon glyphicon-pencil" aria-hidden="true"></i>
      <a data-toggle="collapse" aria-expanded="false" aria-controls={this.props.controls} href={this.props.href} ><span> Edit </span></a>
    </span>
  }
}



class UserInfo extends React.Component {
  constructor(props){
    super(props);
    this.state = {'userInfoContent': ''};
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);

  }

  componentWillReceiveProps(nextProps){
    this.setState({ 'userInfoContent': nextProps.userInfoContent});
  }

  handleChange(e){
    // console.log({ [this.props.userInfo]: e.target.value})
    this.setState({'userInfoContent': e.target.value});
  }



  handleSubmit(e){
    e.preventDefault();
    // cannot get e.target.value, instead use this.state
    // console.log(this.props.userInfo + " is now changed to:" + this.state.userInfoContent);
    this.props.change({ [this.props.userInfo]: this.state.userInfoContent});
  }

  render() {
    return (
      <div >
        <form onSubmit={this.handleSubmit} >
          <div className="form-group">
            <br />
            <small className="text-muted"> Click save button to finish the change. </small>
            <input type="text" className="form-control" value={this.state.userInfoContent} onChange={this.handleChange} />
          </div>
          <div align='right'>
            <input type="submit" className='btn btn-default btn-xs' value='Save' />
          </div>
          <br />
        </form>
      </div>
    );
  }
}

ReactDOM.render(
    <ChangeProfile />,
    document.getElementById('root')
);