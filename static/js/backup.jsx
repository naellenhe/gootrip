"use strict";

class ChangeProfile extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            'name': '', 
            'email': '', 
            'password': '',
            'birthyear': '',
            'zipcode': ''
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

        return (
        <div>
          <dl>
            <dt>Name</dt>
            <dd>{this.state.name}</dd>
            <dt>Email</dt>
            <dd>{this.state.email}</dd>
          </dl>
          {userInfoItem}
        </div>
        );
    }

}


class UserInfo extends React.Component {
  constructor(props){
    super(props);
    this.state = {'userInfoContent': ''};
    this.handleUserInput = this.handleUserInput.bind(this);
  }

  componentWillReceiveProps(nextProps){
    this.setState({ 'userInfoContent': nextProps.userInfoContent});
  }

  handleUserInput(e){

    this.props.change({ [this.props.userInfo]: e.target.value});
    console.log({ [this.props.userInfo]: e.target.value})
    this.setState({'userInfoContent': e.target.value});
  }

  render() {
    return (
      <div>
        <dl>
          <dt>{this.props.userInfo}</dt>
          <dd><input type="text" onChange={this.handleUserInput} value={this.state.userInfoContent} /></dd>
        </dl>
      </div>
    );
  }
}

ReactDOM.render(
    <ChangeProfile />,
    document.getElementById('root')
);