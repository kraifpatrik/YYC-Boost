/// @func YYC_Exception(_message)
/// @desc Base exception.
/// @param {string} [_message] The exception message. Defaults to an empty string.
function YYC_Exception(_message="") constructor
{
	/// @var {string} The exception message.
	/// @readonly
	Message = _message;
}